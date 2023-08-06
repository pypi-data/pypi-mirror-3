import httplib

from five import grok
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, ComponentLookupError
from zope.lifecycleevent.interfaces import (IObjectModifiedEvent,
                                            IObjectMovedEvent)
from zope.event import notify
from z3c.caching.purge import Purge
from z3c.caching.interfaces import IPurgePaths
from plone.registry.interfaces import IRegistry
from silva.core.interfaces import events
from silva.core.interfaces import ISilvaObject, IVersion, IContent, IContainer

from .interfaces import IPurgingService
from .service import registry_map


# Our PURGING strategy for versioned content is thus:
#  * On PublishingEvents (for IVersion), issue a PURGE for the version.  
#    This will generate purge paths for the version's content object
#  * On PublishingEvents, also issue a PURGE for the container when the
#    content is a default (index) document
#  * On ObjectEvents (e.g. modified, removed, etc), issue a PURGE for the
#    container of index documents
#  (the configure.zcml adds IPurgeable to SilvaObject, so ObjectEvents will
#  also issue a PURGE for IContent...)


@grok.subscribe(IVersion, events.IPublishingEvent)
def content_purge(version, event):
    """On PublishingEvents, issue a PURGE to trigger the plone.cachepurging 
       machinery to generate and queue urls to purge ONLY IF there are caching 
       proxies defined AND purging is enabled.  HTTP PURGE requests happen 
       asynchronously after the response is written.
    """
    notify(Purge(version))


@grok.subscribe(IVersion, events.IPublishingEvent)
def index_version_purge(version, event):
    """On PublishingEvents, issue a PURGE event on the container of versioned 
       content which is an index document.
    """
    if version.get_content().is_default():
        notify(Purge(version.get_container()))


@grok.subscribe(IContent, IObjectModifiedEvent)
def index_purge(content, event):
    """When an index document is modified (IObjectModifiedEvent) issue a PURGE 
       on the container.  Since SilvaObject also implements IPurgeable, the 
       content object itself is purged via a different subscriber.
    """
    if content.is_default():
        notify(Purge(content.get_container()))


@grok.subscribe(IContent, IObjectMovedEvent)
def index_purge(content, event):
    """On IObjectMoved, issue a PURGE event on the container of index docs.
       Since SilvaObject also implements IPurgeable, the content object itself 
       is purged via a different subscriber.
    """
    if event.oldParent and content.is_default():
        notify(Purge(content.get_container()))


class VirtualHostingPurgePaths(grok.Adapter):
    """
      An IPurgePaths adapter which translates the path of the context into a
      set of paths to PURGE.
      
      Typically, silva content is not edited on the same domain the content
      is accessed from.  Examples of this situation include editing over
      https (same domain) while site is accessed over http, or editing
      on a special editing domain (e.g. editor.silvasite.com).  When this is
      the case, the absolute url of the content object is not the same as
      the url the content is cached under, and so cannot be used for the 
      purge.

      Making matters more complicated, some sites may have configuration in
      Silva metadata to determine whether the content is served over http or
      https.  [ how to do this, and how to have bethel's custom behavior
      in this package?  a separate zcml file loading it?? ]
      
      Also, some content paths are normalized, e.g. an index document may be
      only accessibly publically by the container's path.  That is, accessing
      /container/index may redirect to /container/, AND accessing /container
      may redirect to /container/ .  Search engines prefer having a SINGLE url
      for content.
    """

    grok.implements(IPurgePaths)
    grok.context(ISilvaObject)
    grok.provides(IPurgePaths)

    def __init__(self, context):
        self.context = context
        
    def getRelativePaths(self):
        """Return the path relative to the Silva root.  Only activated when the
           'Use Domain Translations' option is set on the PurgingService.
           This path will then be translated to a virtualhosting path for
           each domain specified in 'domains'.
        """
        paths = set()
        c = self._get_context()
        
        reg = getUtility(IRegistry, context=c)
        if not reg[registry_map['virtualHosting']]:
            return paths

        #virtualhosting IS enabled, so return the relative path to the 
        # silva root
        path = '/'.join(c.getPhysicalPath())
        sr_path = '/'.join(c.get_root().getPhysicalPath())
        if path.startswith(sr_path):
            path = path[len(sr_path):]
        paths.add(path)
        return paths
    
    def _convert_paths(self, path, mappings):
        """Take the path [ a tuple similar to the result of getPhysicalPath(),
           and translate it into (possibly multiple) urls based on the 
           Purging Services path mappings.
        """
        paths = set()
        
        #algorithm: with a copy of the path:
        #  1) see if there is a key in mappings with that path.  
        #  2) If there is, replace the path with each value, add to set of paths
        #  3) Move the last path component onto a separate list (remained)
        #  4) check mappings for the new (now shorter) path.  
        #  5) If there are mappings, replace the path with each value
        #     adding on the remainder, adding to the set of paths.
        #  6) repeat steps 3-5 until there are no more path components.
        
        pc = list(path[:])
        remainder = []
        while(pc):
            #work backwards searching for all paths in the path mapping
            path_mappings = mappings.get(tuple(pc), [])
            for m in path_mappings:
                if m[-1] != '/':
                    m += '/'
                #rewrite path for each path mapping
                _p = m + '/'.join(remainder)
                paths.add(_p)
            #take the last path component off of pc, insert it into the
            # 0 slot of the remainder
            remainder.insert(0, pc.pop())
        
        return paths
    
    def _get_context(self):
        """Some silva types need to adjust the context prior to path
           computation (e.g. versioned content in particular)
        """
        return self.context
        
    def getAbsolutePaths(self):
        """Use the Purging Service to translate the physical path of the 
           context into the proper PURGE paths, taking into account
           virtual hosting and other caching details.
           
           We use getAbsolutePaths to do this, as relativepaths are altered
           by the IPurgePathRewriter.   For simple vhosting situations, where
           a Silva Root is behind exactly one domain (with maybe http and https)
           this is fine.
        """
        paths = set()
        c = self._get_context()

        #get the service, and the vhost mappings for the service
        try:
            service = getUtility(IPurgingService, context=c)
        except ComponentLookupError: #in case there is no service
            return paths
        
        if not service.get_enabled():
            return paths
        
        mappings = service.get_path_mappings()

        path = c.getPhysicalPath()
        
        paths.update(self._convert_paths(path, mappings))
        
        if IContainer.providedBy(c):
            #also add the '/' version of the container
            path = list(path)
            path.append('')
            paths.update(self._convert_paths(path, mappings))
        return paths


class VersionPurgePaths(VirtualHostingPurgePaths):
    """A VHost Purging Adapter for versions.  The context is adjusted
      so that the urls are generated for the content object and NOT the
      version.
    """
    grok.context(IVersion)
    
    def _get_context(self):
        return self.context.get_content()
