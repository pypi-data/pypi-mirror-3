from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import AUTHMULTIPLUGIN, SF_TEST_OBJECT_TYPE

class TestUserManagmentPlugin(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        # disable the cache for tests in TestAuthenticationPlugin
        self.plugin.ZCacheable_setManagerId(None)
        
        self.acl = self.portal.acl_users
        self.plugins = self.acl.plugins
        self.usermgmt = getattr(self.acl, AUTHMULTIPLUGIN)
        
        self.username = 'plonetestcase'
        self.lastname = 'McPlonesonUser'
        self.password = 'password'
    
    def testChangeUserPassword(self):
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
        
        # update the password
        self.usermgmt.doChangeUser(self.username, "secret")
        
        # query and assert that the user's password is updated
        user_list = self.toolbox.query(
            "SELECT Password__c FROM %s WHERE UserName__c='%s'" % (
                SF_TEST_OBJECT_TYPE,
                self.username
                )
            )
        self.assertEqual("secret", user_list['records'][0]['Password__c'])
    
    def testDoChangeUserGracefullyHandlesMultiLogins(self):
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
        
        # now create a second user with the same username
        res2 = self.toolbox.create(obj)
        if not res2[0]['success'] and res2[0]['errors'][0]['statusCode'] == 'DUPLICATE_VALUE':
            # second user creation was disallowed due to duplicate user id;
            # so the issue this test is for shouldn't be a problem
            return
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId2 = res2[0]['id']
        self._toCleanUp.append(sfUserId2)
        
        # attempt a password update which will fail
        # due to multiple Salesforce.com contacts w/ the
        # same login, but hopefully not keel over and die...
        self.usermgmt.doChangeUser(self.username, "secret")
        
        # query and assert that the Contact passwords haven't been updated
        user_list = self.toolbox.query(
            "SELECT Password__c FROM %s WHERE UserName__c='%s'" % (
                SF_TEST_OBJECT_TYPE,
                self.username)
            )
        for i in range(len(user_list['records'])):
            self.assertNotEqual("secret", user_list['records'][i]['Password__c'])
    
    def testAllowPasswordSet(self):
        self.failIf(self.usermgmt.allowPasswordSet(self.username))
        
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
        
        self.failUnless(self.usermgmt.allowPasswordSet(self.username))
        
    def testAllowDeletePrincipal(self):
        self.failIf(self.usermgmt.allowDeletePrincipal(self.username))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserManagmentPlugin))
    return suite
