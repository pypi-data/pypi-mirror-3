from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import AUTHMULTIPLUGIN, PROJECTNAME
from zExceptions import BadRequest

class TestProductReInstallation(SalesforceAuthPluginTestCase):
    """ Ensure that our policy product reinstalls politely -- or --
        a host of things that can go wrong if you're not careful with
        Generic Setup
    """
    def afterSetUp(self):                   
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        self.properties = self.portal.portal_properties
        self.qi         = self.portal.portal_quickinstaller
    
    def testSettingsNotClobberedOnReinstall(self):
        """ This test confirms that the auth plugin's settings will not be deleted
            if the product is simply reinstalled.
        """
        acl = getattr(self.portal.acl_users, AUTHMULTIPLUGIN)
        acl.setEncryptionAlgorithm('sha')
        
        # reinstall our product
        self.setRoles(['Manager'])
        if self.qi.isProductInstalled('collective.salesforce.authplugin'):
            self.qi.reinstallProducts(products=['collective.salesforce.authplugin',])
                                                              
        # get the plugin again (in case it was replaced) and make sure the setting is the same
        acl = getattr(self.portal.acl_users, AUTHMULTIPLUGIN)
        self.assertEqual(acl.getEncryptionAlgorithm(), 'sha', 'Looks like the plugin settings got clobbered on reinstall.')
    
    def testDontAddSFAuthPluginIfSFAuthPluginAlreadyExists(self):
        """If there's already a salesforceauthplugin object in acl_users,
           we shouldn't try to create another one
        """
        try :
            self.qi.reinstallProducts(PROJECTNAME)
        except BadRequest, msg:
            self.fail("Should reinstall cleanly, but got error: %s" % msg)
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductReInstallation))
    return suite
