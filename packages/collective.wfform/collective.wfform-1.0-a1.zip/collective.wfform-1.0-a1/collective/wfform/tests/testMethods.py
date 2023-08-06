import unittest2 as unittest

from base import INTEGRATION_TESTING
from utils.dummy_class import DummyClass

class TestInstallation(unittest.TestCase):
    """Ensure product is properly installed"""
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.content_type = DummyClass('dummy')

    def testBrowserLayerRegistered(self):
        interface = self.content_type.getSchemaForTransition('empty')
        assert interface.__class__.__name__ == 'InterfaceClass'
