from five import grok
from zope.component import getUtility, queryUtility, getAdapters
from zope.event import notify
from DateTime import DateTime
from zope.publisher.browser import TestRequest
from ZPublisher.pubevents import PubStart, PubSuccess
from zope.annotation.interfaces import IAttributeAnnotatable, IAnnotations
from plone.registry.interfaces import IRegistry
from plone.cachepurging.hooks import KEY as URL_QUEUE_KEY
from plone.cachepurging.interfaces import IPurger
from plone.cachepurging.utils import getPathsToPurge
from z3c.caching.purge import Purge
from z3c.caching.interfaces import IPurgePaths

from PurgingTestCase import PurgingTestCase
from bethel.silva.purge.interfaces import IPurgingService
from bethel.silva.purge.service import registry_map
from bethel.silva.purge import testing


class BetterTestRequest(TestRequest):
    """Stupid TestRequest does not support annotations.  Seems everything has
       annotations these days, which makes writing tests impossible.  Add
       back in support for request.other, so annotations are possible
    """
    grok.implements(IAttributeAnnotatable)

    def __init__(self, *args, **kw):
        self.other = {}
        super(BetterTestRequest, self).__init__(*args, **kw)
    
    def __setitem__(self, key, value):
        self.other[key] = value
        
    def keys(self):
        k = set(super(BetterTestRequest, self).keys())
        k.add(self.other.keys())
        return list(k)
        
    def get(self, key, default=None):
        marker = object()
        result = super(BetterTestRequest, self).get(key, marker)
        if result is not marker:
            return result
        
        return self.other.get(key, default)


class PurgeTestCase(PurgingTestCase):
    
    def setUp(self):
        super(PurgeTestCase, self).setUp()
        #not doing anything here, yet
        self.browser = self.layer.get_browser()
        self.browser.options.handle_errors = False
        self.root = self.layer.get_application()
        self.doc = self.layer.addObject(self.root,
                                        'Document',
                                        'doc',
                                        product='SilvaDocument',
                                        title="doc")
        self.now = DateTime()
        
        self.layer.addObject(self.root,
                             'Folder',
                             'f',
                             title="f")
        self.layer.addObject(self.root.f,
                             'Document',
                             'index',
                             product='SilvaDocument',
                             title="index")
        
        self.service = getUtility(IPurgingService, context=self.root)
        config = {('','root'): ['/blah/', '/blah2']}
        self.service.set_path_mappings(config)
        self.service.set_enabled(True)
        
        #ensure purging is enabled in the registry
        reg = getUtility(IRegistry, context=self.root)
        reg[registry_map['enabled']] = True
        reg[registry_map['cachingProxies']] = ('http://localhost:6081/',)
        
    def test_notify(self):

        #simple test to verify that Purge events are actually occurring
        version = self.doc.get_editable()
        notify(Purge(version))
        
        #now service should have a test_counter, which we use to
        # validate an event occurred.  This is event handler is in
        # tests.grok.purge_events
        self.assertEquals(self.service.test_counter.pop(),
                          version)
        
        #reset counter
        self.service.test_counter = []
        
        #publishing the document should add this version to the test_counter
        # (this verifies that the purge occurs on publishing events)
        self.doc.set_unapproved_version_publication_datetime(self.now)
        self.doc.approve_version()  #publish
        
        #note that two contentpublishingevents happen when approve_version is 
        # called, so the version is actually in the list twice
        self.assertListEqual(self.service.test_counter, [version, version])
        
    def test_publishing_notify(self):
        #test publishing notify, using a mocked request to purge events
        # are handled and not short-circuited (a request is required for
        # the purge url annotations)
        
        version = self.doc.get_editable()
        request = BetterTestRequest()

        annotations = IAnnotations(request)
        self.assertFalse(annotations.has_key(URL_QUEUE_KEY))

        #starting the request and approving content will cause the queue
        # to be populated with urls to purge
        
        notify(PubStart(request))
        self.doc.set_unapproved_version_publication_datetime(self.now)
        self.doc.approve_version()  #publish
        
        #just verify there are things in the queue
        annotations = IAnnotations(request)
        self.assertTrue(annotations.has_key(URL_QUEUE_KEY))
        queue = IAnnotations(request)[URL_QUEUE_KEY]
        self.assertTrue(len(queue) > 0)
        
        notify(PubSuccess(request))
        
        #now stop the purger threads
        purger = queryUtility(IPurger)
        purger.stopThreads(wait=True)
        
    def test_publishing_notify_index(self):
        
        version = self.doc.get_editable()
        request = BetterTestRequest()

        annotations = IAnnotations(request)
        self.assertFalse(annotations.has_key(URL_QUEUE_KEY))

        notify(PubStart(request))

        #trigger a purge on the index of a container, inspect the url
        # annotations to see that the index and it's container are listed
        # (in their various forms)
        self.root.f.index.set_unapproved_version_publication_datetime(self.now)
        self.root.f.index.approve_version()  #publish
        
        annotations = IAnnotations(request)
        self.assertTrue(annotations.has_key(URL_QUEUE_KEY))
        queue = IAnnotations(request)[URL_QUEUE_KEY]
        self.assertTrue('/blah2/f/index' in queue)
        self.assertTrue('/blah2/f/' in queue)
        self.assertTrue('/blah2/f' in queue)
        self.assertTrue('/blah/f/index' in queue)
        self.assertTrue('/blah/f/' in queue)
        self.assertTrue('/blah/f' in queue)

        notify(PubSuccess(request))
        
        #now stop the purger threads
        purger = queryUtility(IPurger)
        purger.stopThreads(wait=True)
    
    def test_paths_to_purge(self):
        #test the bethel.silva.purge and the IPurgePaths adapter

        paths = set()
        item = self.doc.get_editable()
        for name, pathProvider in getAdapters((item,),
                                              IPurgePaths):
            paths.update(set(pathProvider.getRelativePaths()))
            paths.update(set(pathProvider.getAbsolutePaths()))
            
        self.assertTrue('/blah2/doc' in paths)
        self.assertTrue('/blah/doc' in paths)
        
        #check IPurgePaths on a container (should have both '/' and no '/')
        paths = set()
        for name, pathProvider in getAdapters((self.root.f,),
                                              IPurgePaths):
            paths.update(set(pathProvider.getRelativePaths()))
            paths.update(set(pathProvider.getAbsolutePaths()))
        
        self.assertTrue('/blah2/f' in paths)
        self.assertTrue('/blah2/f/' in paths)
        self.assertTrue('/blah/f' in paths)
        self.assertTrue('/blah/f/' in paths)

    def test_service_disabled(self):
        #verify that no paths are added when path translations are disabled.
        self.service.set_enabled(False)
        paths = set()
        item = self.doc.get_editable()
        for name, pathProvider in getAdapters((item,),
                                              IPurgePaths):
            paths.update(set(pathProvider.getRelativePaths()))
            paths.update(set(pathProvider.getAbsolutePaths()))

        #only path in here should be from the traverser
        self.assertListEqual(['/root/doc/0'], list(paths))

    def test_virtualhosting(self):
        #test the plone.cachepurging virtualhosting support
        reg = getUtility(IRegistry, context=self.root)
        reg[registry_map['virtualHosting']] = True
        reg[registry_map['domains']] = ('http://example.com:80',
                                        'https://example.com:443')

        #don't clutter the set
        self.service.set_enabled(False)

        paths = set()
        item = self.doc.get_editable()
        for name, pathProvider in getAdapters((item,),
                                              IPurgePaths):
            paths.update(set(pathProvider.getRelativePaths()))
            paths.update(set(pathProvider.getAbsolutePaths()))

        #only paths in here are from the traverser and the relative path
        # from the silva root
        self.assertListEqual(['/root/doc/0','/doc'], paths)
        
        #request needs VIRTUAL_URL and VIRTUAL_URL_PARTS and 
        # VirtualRootPhysicalPath
        request = BetterTestRequest(environ={'VIRTUAL_URL_PARTS': ('a','b'),
                                             'VirtualRootPhysicalPath': ('','root'),
                                             'VIRTUAL_URL': 'http://example.com/doc'
                                             }
                                    )
        paths = list(getPathsToPurge(item, request))
        
        #there's more in the paths list (from the traverser), so test just the
        # two paths we care about
        self.assertTrue('/VirtualHostBase/http/example.com:80/root/VirtualHostRoot/doc' in paths)
        self.assertTrue('/VirtualHostBase/https/example.com:443/root/VirtualHostRoot/doc' in paths)

    def test_get_utility(self):
        #simple test of using get/queryUtility
        ps = queryUtility(IPurgingService, context=self.root)
        self.assertFalse(ps is None)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PurgeTestCase))
    return suite