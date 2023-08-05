from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN, CACHEHANDLER

class TestProductInstall(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        self.qi = self.portal.portal_quickinstaller
        self.acl = self.portal.acl_users
        self.implemented_plugin_types = ("IAuthenticationPlugin","IUserEnumerationPlugin","IPropertiesPlugin",
                                    "IUpdatePlugin","IUserAdderPlugin","IUserManagement",)
    
    def testProductQuickInstallableAndInstalled(self):
        self.failUnless(self.qi.isProductInstallable(PROJECTNAME))
        self.failUnless(self.qi.isProductInstalled(PROJECTNAME))
    
    def testInstallationCreatesPASObjects(self):
        """Make sure our installation code adds the salesforceauthplugin
        """
        self.failUnless(AUTHMULTIPLUGIN in self.acl.objectIds())
    
    def testAppropriatePluginTypesActivatedOnInstall(self):
        """This test insures that the desired plugin types have
           been activated upon product installation.
        """
        for iface in self.implemented_plugin_types:
            
            # make sure our plugin shows up in the active list
            self.failUnless(AUTHMULTIPLUGIN in self.acl.plugins.getAllPlugins(iface)['active'],
                "Plugin %s hasn't been activated upon install for plugin type %s" % (AUTHMULTIPLUGIN, iface))
            
            # ... and just to be safe
            self.failIf(AUTHMULTIPLUGIN in self.acl.plugins.getAllPlugins(iface)['available'],
                "Plugin %s is listed as available for use upon install for plugin type %s" % (AUTHMULTIPLUGIN, iface))
    
    def testAuthPluginPrioritizedOnInstallForImplementedPluginTypes(self):
        """This test insures that our plugin takes priority
           over all other plugin options.  We do and will aim to 
           provide warnings and damage control for improper configurations
           and PAS happily moves onto the next available plugin.
        """
        for iface in self.implemented_plugin_types:
            self.assertEqual(AUTHMULTIPLUGIN, self.acl.plugins.getAllPlugins(iface)['active'][0],
                "Plugin %s isn't the first used for plugin type %s" % (AUTHMULTIPLUGIN, iface))
    
    def testAuthPluginSpecificZCacheManagerAvailable(self):
        """Our installation code *should* automatically create a ZCacheManager
           for use with our plugin.  This test ensures that's the case.
        """
        self.failUnless('SalesforceAuthPluginCache' in [zcache_manager['id'] for zcache_manager \
            in self.acl.ZCacheable_getManagerIds()])
    
    def testRAMCacheAssociatedWithPlugin(self):
        """Our installation code *should* automatically set up and associates a RAM cache
           with the Salesforce Auth Plugin.  This test ensures that's the case.
        """
        self.failUnless(self.plugin.ZCacheable_enabled())
        self.assertEqual(CACHEHANDLER, self.plugin.ZCacheable_getManagerId())
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
