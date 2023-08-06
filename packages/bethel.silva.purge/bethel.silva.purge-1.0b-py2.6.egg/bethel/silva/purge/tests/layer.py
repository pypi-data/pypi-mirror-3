from Products.Silva.testing import SilvaLayer
import transaction

class PurgeLayer(SilvaLayer):
    
    default_products = SilvaLayer.default_products + ['SilvaDocument']
    
    default_packages = SilvaLayer.default_packages + ['zope.annotation']
    
    def _install_application(self, app):
        """ install the silva event extension """
        super(PurgeLayer, self)._install_application(app)
        app.root.service_extensions.install('bethel.silva.purge')
        self.grok('bethel.silva.purge.tests.grok')
        
    def addObject(self, container, type_name, id, product='Silva', **kw):
        getattr(container.manage_addProduct[product],
                'manage_add%s' % type_name)(id, **kw)
        # gives the new object a _p_jar ...
        transaction.savepoint()
        return getattr(container, id)
        