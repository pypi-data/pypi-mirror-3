from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN
from collective.salesforce.authplugin.plugins.sfausermanager import SalesforceAuthMultiPlugin
from collective.salesforce.authplugin.interfaces import IUserManagementPluginPropertyManager, IMappingUI
from zope.interface.verify import verifyObject, verifyClass

class TestInterfaces(SalesforceAuthPluginTestCase):
    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        self.acl = self.portal.acl_users
        self.plugins = self.acl.plugins
        self.authentication = getattr(self.acl, AUTHMULTIPLUGIN)
    
    def testClassImplements(self):
        # verify IEdition
        self.failUnless(IUserManagementPluginPropertyManager.implementedBy(SalesforceAuthMultiPlugin))
        self.failUnless(IMappingUI.implementedBy(SalesforceAuthMultiPlugin))
    
    def testClassVerifies(self):
        self.failUnless(verifyClass(IUserManagementPluginPropertyManager, SalesforceAuthMultiPlugin))
        self.failUnless(verifyClass(IMappingUI, SalesforceAuthMultiPlugin))
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInterfaces))
    return suite
