from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN

from Products.PloneTestCase import PloneTestCase
default_user = PloneTestCase.default_user

class TestProductUnInstallation(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        self.qi = self.portal.portal_quickinstaller
        self.acl = self.portal.acl_users
        
        # uninstall our product for test suite
        if self.qi.isProductInstalled(PROJECTNAME):
            self.setRoles(['Manager',])
            self.qi.uninstallProducts([PROJECTNAME,])
            self.login(default_user)
    
    def testProductInstallableButNotInstalled(self):
        self.failIf(self.qi.isProductInstalled(PROJECTNAME))
        self.failUnless(self.qi.isProductInstallable(PROJECTNAME))
    
    def testUninstallationRemovesPASObjects(self):
        self.failIf(AUTHMULTIPLUGIN in self.acl.objectIds())
    
    def testAuthPluginSpecificZCacheManagerRemovedOnUninstallation(self):
        """Our uninstallation code *should* remove the ZCacheManager
           for use with our plugin.  This test ensures that's the case.
        """
        self.failIf('SalesforceAuthPluginCache' in [zcache_manager['id'] for zcache_manager \
            in self.acl.ZCacheable_getManagerIds()])
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductUnInstallation))
    return suite
