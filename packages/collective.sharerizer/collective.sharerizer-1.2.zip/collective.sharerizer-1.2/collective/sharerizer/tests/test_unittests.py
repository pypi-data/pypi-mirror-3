import unittest
from Products.CMFCore.utils import getToolByName
from collective.sharerizer.tests.base import FunctionalTestCase

class TestUninstallation(FunctionalTestCase):

    def testUninstallationLeavesNoCruft(self):
        # GS doesn't remove our changes to portal_properties or
        # portal_controlpanel
                
        # uninstall our product
        # XXX: for some reason, our uninstall function isn't getting called
        # during testing, but is during normal use. 
        qi = getToolByName(self.portal, "portal_quickinstaller")
        qi.uninstallProducts(products=['collective.sharerizer',])
        
        # no property sheet in portal_properties
        portal_properties = getToolByName(self.portal, "portal_properties")
        self.failIf(hasattr(portal_properties, 'sharerizer'))
        
        # no configlet registered
        controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.failIf(hasattr(portal_properties, 'sharerizer'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUninstallation))
    return suite
