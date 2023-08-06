from PurgingTestCase import PurgingTestCase

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from bethel.silva.purge.service import registry_map
from bethel.silva.purge.interfaces import IPurgingService


class ServiceTestCase(PurgingTestCase):
    #goal is to add an event and get it listed in a viewer
    
    def setUp(self):
        super(PurgingTestCase, self).setUp()
        #not doing anything here, yet
        self.browser = self.layer.get_browser()
        self.browser.options.handle_errors = False
        self.root = self.layer.get_application()
        
    def test_is_installed(self):
        self.assertTrue(hasattr(self.root.aq_explicit, 'service_purging'))
        
    def test_registry_defaults(self):
        reg = getUtility(IRegistry, context=self.root)
        self.assertFalse(reg[registry_map['enabled']])
        
    def test_managemain(self):
        #make sure that accessing manage_main redirects to the real
        # management screen
        b = self.browser
        b.login('manager')
        code = b.open('/root/service_purging/manage_main')
        self.assertEquals(b.url,
                          '/root/service_purging/managepurging')
        
    def test_zmi_form(self):
        #test configuring purging service via the zmi form
        b = self.browser
        url = '/root/service_purging'
        p = self.root.service_purging

        #try to access main mgmt form, should fail
        b.login('dummy')
        code = b.open(url + '/managepurging')
        self.assertEquals(code, 401)
        
        b.login('manager')
        b.open(url + '/managepurging')
        
        #add a field to the cachingproxies (need to click the 'add' button)
        f = b.get_form(name='purging')
        f.get_control('purging.field.cachingProxies.add').click()

        #page submitted; get form again, and add value to cachingProxies
        f = b.get_form(name='purging')
        f.get_control('purging.field.cachingProxies.field.0').value='http://localhost:6081'
        f.get_control('purging.field.enabled').checked = True
        f.submit(name="purging.action.save-configuration")
        
        #verify value was added to the registry
        reg = getUtility(IRegistry, context=self.root)
        self.assertTrue(reg[registry_map['enabled']])
        self.assertListEqual(reg[registry_map['cachingProxies']],
                             ['http://localhost:6081'])
        
        #disable purging
        f = b.get_form(name='purging')
        f.get_control('purging.field.enabled').checked = False
        f.submit(name="purging.action.save-configuration")
        self.assertFalse(reg[registry_map['enabled']])
        
        
        f = b.get_form(name='purging')
        f.get_control('purging.field.use_path_mapping').checked = True
        #test path mapping.  Saving this field should:
        # 1) normalize paths (remove trailing '/')
        # 2) remove duplicate values
        # 3) allow multiple values for the same path
        f.get_control('purging.field.path_mapping').value = (
            '/silva/www/ /blah\r\n'
            '/silva/www /blah\r\n'
            '/silva/www /blah2\r\n'
            '/silva/asdf /blinky'
            )
        
        f.submit(name="purging.action.save-configuration")
        service = getUtility(IPurgingService, context=self.root)
        _m = service._path_mapping
        self.assertTrue(('','silva','www') in _m)
        self.assertTrue(('','silva','www','') not in _m)
        self.assertTrue(('','silva','asdf') in _m)
        self.assertListEqual(list(_m[('','silva','www')]), list(set(['/blah', '/blah2'])))
        self.assertListEqual(list(_m[('','silva','asdf')]), ['/blinky'])
        
        self.assertTrue(service.get_enabled())
        
        #turn on domain translations
        f = b.get_form(name='purging')
        f.get_control('purging.field.domains.add').click()
        f = b.get_form(name='purging')
        f.get_control('purging.field.domains.add').click()
        
        f = b.get_form(name='purging')
        f.get_control('purging.field.virtualHosting').checked = True
        f.get_control('purging.field.domains.field.0').value='http://example.com:80'
        f.get_control('purging.field.domains.field.1').value='https://example.com:443'
        
        code = f.submit(name="purging.action.save-configuration")
        self.assertEqual(code, 200)
        
        self.assertTrue(reg[registry_map['virtualHosting']])
        self.assertListEqual(reg[registry_map['domains']],
                             ['http://example.com:80',
                              'https://example.com:443']
                             )
        


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ServiceTestCase))
    return suite