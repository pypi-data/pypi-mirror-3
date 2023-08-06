from Products.Silva.tests import SilvaTestCase

from Products.Silva.testing import TestCase

import bethel.silva.purge
import layer

class PurgingTestCase(TestCase):
    
    layer = layer.PurgeLayer(bethel.silva.purge,
                             zcml_file='configure.zcml')
    
    