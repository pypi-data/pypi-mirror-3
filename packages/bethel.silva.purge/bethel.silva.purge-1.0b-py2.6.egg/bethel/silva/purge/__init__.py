from zope.interface import Interface
from zope.component import getUtility, provideAdapter, queryUtility
from OFS.SimpleItem import SimpleItem

from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from plone.cachepurging.interfaces import ICachePurgingSettings

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller

silvaconf.extension_name("bethel.silva.purge")
silvaconf.extension_title("Silva Purging Service")

class ZRegistry(SimpleItem, Registry):
    """a plone.registry made a zope object"""
    
    def __init__(self, id):
        super(ZRegistry, self).__init__()
        self.id = id


class Installer(DefaultInstaller):
    """Create purging service in the root on install"""
    
    def install_custom(self, root):
        from service import PurgingService as PS
        if PS.default_service_identifier not in root.objectIds():
            factory = root.manage_addProduct['bethel.silva.purge']
            factory.manage_addPurgingService()
        
        #install the plone.registry into the root, register it as a
        # service (utility), and add the cache purging settings to the
        # registry
        reg_id = 'plone.registry.Registry'
        if not hasattr(root.aq_explicit, reg_id):
            reg = ZRegistry(reg_id)
            reg = silvaconf.utils.registerService(root, 
                                                  reg.id, 
                                                  reg,
                                                  IRegistry)
            reg.registerInterface(ICachePurgingSettings)
            #cache purge is disabled by default
            reg['plone.cachepurging.interfaces.ICachePurgingSettings.enabled'] = False
    
    def uninstall_custom(self, root):
        """Ideally one would remove the service on uninstall, but this is
           also called during a refresh, and we don't want to loose 
           any configurations, so don't do anything
        """


class IPurgeExtension(Interface):
    """Marker interface for our extension.
    """

install = Installer("bethel.silva.purge", IPurgeExtension)

