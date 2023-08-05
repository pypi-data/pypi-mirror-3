import sys
from beatbox import SoapFaultError

from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import AUTHMULTIPLUGIN, SF_TEST_OBJECT_TYPE

class TestAuthenticationPlugin(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        # disable the cache for tests in TestAuthenticationPlugin
        self.plugin.ZCacheable_setManagerId(None)
        
        self.acl = self.portal.acl_users
        self.authentication = getattr(self.acl, AUTHMULTIPLUGIN)
        
        self.username = 'joe'
        self.lastname = 'plonetestuser'
        self.password = 'password'
        self.email    = 'email@example.com'
    
    def testAuthenticateCredentials(self):
        """Ensure that authentication can happen
        """
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
        )
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # ensure they can login
        auth = self.authentication.authenticateCredentials({'login': self.username,
                                                          'password': self.password})
        self.assertEqual(auth, (self.username, self.username))
        
        # if invalid credentials are supplied, make sure None is returned,
        # rather than raising an exception
        auth = self.authentication.authenticateCredentials({'login': self.username,
                                                            'password': 'foobar'})
        self.failUnless(auth is None)

    def testAuthenticatingSessionCredentialsDoesntHitSalesforce(self):
        # if the credentials don't have a login and password, we should get None
        # without Salesforce ever being queried.  To test this we'll temporarily
        # get rid of the base connector so that access to SF will fail
        self.setRoles(['Manager'])
        self.portal.manage_delObjects(['portal_salesforcebaseconnector'])
        
        auth = self.authentication.authenticateCredentials({'login': 'foo'})
        self.assertEqual(auth, (None, None))
        
        auth = self.authentication.authenticateCredentials({'password': 'bar'})
        self.assertEqual(auth, (None, None))
    
    def testCanAuthenticateAgainstLeadSFObjectType(self):
        # user dictionary, to run this test the lead object
        # needs to have a username and password custom field
        # otherwise we catch the exception and pass
        obj = dict(type = 'Lead',
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            LeadSource = 'SFA Test Suite',
            Company = '[not provided]',
        )
        try:
            # create our user
            res = self.toolbox.create(obj)
            # add our user to the _toCleanUp list for removal via the 
            # salesforce api regardless of success/failure
            sfUserId = res[0]['id']
            self._toCleanUp.append(sfUserId)
        
            # can't login just yet...
            auth = self.authentication.authenticateCredentials({'login': self.username,
                                                              'password': self.password})
            self.failIf(auth)
        
            # because we need to update our sfObjectType
            self.authentication.setSFObjectType('Lead')
            self.authentication.setLocalToSFMapping({}, mapType='properties')
            
            # now make sure we can login
            auth = self.authentication.authenticateCredentials({'login': self.username,
                                                              'password': self.password})
            self.assertEqual(auth, (self.username, self.username))
        
        except SoapFaultError:
            print >> sys.stderr, ("WARNING: For this test to successfully run, you need to add the following custom fields"
                                  " to the Lead object: UserName__c and Password__c.  See README.txt --> 'Running Tests' "
                                  "for more.")
    
    def testAuthAgainstSelfConfiguredAuthFieldMapping(self):
        """By default, the auth plugin has no username, password
           mapping for authentication.  We ensure that we're
           update the mapping fields and continue to authenticate.
        """
        dept = 'Information Technology'
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            Department = dept
        )
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # with the default auth mapping, we fail authentication
        auth = self.authentication.authenticateCredentials({'login': self.lastname,
                                                          'password': dept})
        self.failIf(auth)
        
        # however, we configure authentication against LastName as login
        # Department as password
        auth_config_mapping = {'username':'LastName', 'password':'Department'}
        self.authentication.setLocalToSFMapping(auth_config_mapping, mapType='auth')
        
        # try authenticating again
        auth = self.authentication.authenticateCredentials({'login': self.lastname,
                                                          'password': dept})
        self.assertEqual(auth, (self.lastname, self.lastname))
    
    def testAuthenticateCredentialsWithCustomSOQLCondition(self):
        """Ensure that authentication accounts for an
           extra auth condition clause
        """
        # the extra condition we're going to use to "protect" authentication
        soqlClause = """Email like '%@example.com'"""
        
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
        )
        # create our user as above
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # test, setup a custom SOQL condition, test again
        self.failIf(self.authentication.getAuthConditionClause())
        self.authentication.setAuthConditionClause(soqlClause)
        self.failUnless(self.authentication.getAuthConditionClause())
        
        # what about adding an invalid SOQL condition?
        # bad field should leave the value same as before
        self.authentication.setAuthConditionClause("""BadField like '%@example.com'""")
        self.failUnless(self.authentication.getAuthConditionClause() == soqlClause)
        # invalid query should leave the value same as before
        self.authentication.setAuthConditionClause("""bad query""")
        self.failUnless(self.authentication.getAuthConditionClause() == soqlClause)
        
        # now we can't login they can login
        auth = self.authentication.authenticateCredentials({'login': self.username,
                                                          'password': self.password})
        self.failIf(auth)
        
        # update the user
        updateData = dict(type = SF_TEST_OBJECT_TYPE,
                          Id=sfUserId,
                          Email = self.email)
        
        self.toolbox.update(updateData)
        
        # now ensure we *can* login
        auth = self.authentication.authenticateCredentials({'login': self.username,
                                                          'password': self.password})
        self.assertEqual(auth, (self.username, self.username))
    
    def testDefaultAuthMappingReturnsNone(self):
        # as would be the case immediately after installation,
        # we wipe out the test suite's auth field mapping
        self.authentication.setLocalToSFMapping({}, mapType='auth')
        
        # ensure that no exception is raised when we're operating as an 
        # IAuthenticationPlugin without any auth field mapping and
        # that autentication fails
        auth = self.authentication.authenticateCredentials({'login': self.username, 'password': self.password,})
        self.failIf(auth)
    


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAuthenticationPlugin))
    return suite
