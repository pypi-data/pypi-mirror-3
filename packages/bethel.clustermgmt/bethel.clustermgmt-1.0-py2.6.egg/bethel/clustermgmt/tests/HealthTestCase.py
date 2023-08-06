from Products.Silva.testing import TestCase

import bethel.clustermgmt
import layer

class HealthTestCase(TestCase):
    
    layer = layer.HealthLayer(bethel.clustermgmt,
                              zcml_file='configure.zcml')