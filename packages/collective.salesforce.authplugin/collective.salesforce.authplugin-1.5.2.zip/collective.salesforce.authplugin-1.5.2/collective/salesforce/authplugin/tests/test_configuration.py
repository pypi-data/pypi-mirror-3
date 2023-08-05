from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import AUTHMULTIPLUGIN

from zope.component import getAllUtilitiesRegisteredFor
from collective.salesforce.authplugin.encrypt import IEncrypter

class TestUserManagementPropertyManager(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        self.acl = self.portal.acl_users
        self.plugins = self.acl.plugins
        self.authentication = getattr(self.acl, AUTHMULTIPLUGIN)
        encrypters = [encrypter.name for encrypter in getAllUtilitiesRegisteredFor(IEncrypter)]
        self.validEncryptionAlgorithms = encrypters
    
    def testConfOfSFObjectType(self):
        # By default, we should always be a contact 
        # (this or a lead are the standard use-cases)
        self.assertEqual('Contact',self.authentication.getSFObjectType())
        
        # Now let's set a new sfobject type
        self.authentication.setSFObjectType('Lead')
        self.assertEqual('Lead',self.authentication.getSFObjectType())
        
        # Throw some spaces in there for good measure
        self.authentication.setSFObjectType(' Lead ')
        self.assertEqual('Lead',self.authentication.getSFObjectType())
    
    def testConfOfAuthFieldMappings(self):
        # setup a reasonable auth mapping
        auth_config_mapping = {
            'password':'SomePasswordField__c',
            'username':'SomeUserNameField__c',
        }
        self.authentication.setLocalToSFMapping(auth_config_mapping, mapType='auth')
        
        # ensure that the plugin was correctly configured
        self.assertEqual(auth_config_mapping, 
            self.authentication.getLocalToSFMapping(mapType='auth'))
    
    def testConfOfPropFieldMappings(self):
        # setup a reasonable prop mapping that's not
        # the same as our setup in base.py --> afterSetup
        prop_config_mapping = {
            'assistant_name':'MyAssistantName__c',
            'department':'MyDepartment__c',
        }
        
        self.authentication.setLocalToSFMapping(prop_config_mapping, mapType='properties')
        
        # ensure that the plugin was correctly configured
        self.assertEqual(prop_config_mapping, 
            self.authentication.getLocalToSFMapping(mapType='properties'))
    
    def testConfOfAuthFieldMappingLeavesPropMappingAlone(self):
        currPropertyMapping = self.authentication.getLocalToSFMapping()
        
        auth_config_mapping = {
            'password':'SomeCompletelyBogusPasswordField__c',
            'username':'SomeCompletelyBogusUserNameField__c',
        }
        self.authentication.setLocalToSFMapping(auth_config_mapping, mapType='auth')
        
        # protects against faulty code setting both field mappings at once
        self.assertEqual(currPropertyMapping, self.authentication.getLocalToSFMapping(mapType='properties'))
    
    def testConfOfPropFieldMappingLeavesAuthMappingAlone(self):
        currAuthMapping = self.authentication.getLocalToSFMapping(mapType='auth')

        prop_config_mapping = {
            'assistant_name':'MyAssistantName__c',
            'department':'MyDepartment__c',
        }
        self.authentication.setLocalToSFMapping(prop_config_mapping, mapType='properties')

        # protects against faulty code setting both field mappings at once
        self.assertEqual(currAuthMapping, self.authentication.getLocalToSFMapping(mapType='auth'))

    def testConfOfAuthConditionClause(self):
        # By default this is empty
        self.failIf(self.authentication.getAuthConditionClause())
        
        # Now we update this
        self.authentication.setAuthConditionClause("Email like '%@example.com'")
        self.assertEqual("Email like '%@example.com'", self.authentication.getAuthConditionClause())
        
        # Throw in some spaces again for good measure
        self.authentication.setAuthConditionClause(" FirstName like 'Jo%' ")
        self.assertEqual("FirstName like 'Jo%'", self.authentication.getAuthConditionClause())
        
        # make sure we can set it back to an empty string
        res = self.authentication.setAuthConditionClause('')
        self.failUnless(res)
        self.assertEqual('', self.authentication.getAuthConditionClause())
        
        
    def testIsValidEncryptionAlgorithm(self):
        for alg in self.validEncryptionAlgorithms:
            self.failUnless(alg in self.authentication.listValidEncryptionAlgorithms(), 
                "%s should be valid encryption algorithm" % alg)
            
        self.assertFalse('somebogusone' in self.authentication.listValidEncryptionAlgorithms(), 
                "%s is not a valid encryption algorithm" % alg)
                
        
    def testSetEncryptionAlgorithm(self):
        # test default encryption (this is 'plain' for tests)
        self.assertEquals('plain', self.authentication.getEncryptionAlgorithm())
        
        # test our plugin's default 
        self.authentication.setEncryptionAlgorithm()
        self.assertEquals('md5', self.authentication.getEncryptionAlgorithm())

        for alg in self.validEncryptionAlgorithms:
            self.failUnless(self.authentication.setEncryptionAlgorithm(alg), 
                "%s should be valid encryption algorithm" % alg)
            self.assertEquals(alg, self.authentication.getEncryptionAlgorithm())
            
        self.assertFalse(self.authentication.setEncryptionAlgorithm('somebogusone'), 
                "%s is not a valid encryption algorithm" % alg)
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserManagementPropertyManager))
    return suite
