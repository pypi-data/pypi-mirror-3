from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN, SF_TEST_OBJECT_TYPE

class TestUserEnumerationPlugin(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        # disable the cache for tests in TestAuthenticationPlugin
        self.plugin.ZCacheable_setManagerId(None)
        
        self.acl = self.portal.acl_users
        self.plugins = self.acl.plugins
        self.userenumerator = getattr(self.acl, AUTHMULTIPLUGIN)
        self.username = 'plonetestcase'
        self.password = 'password'
    
    def testEnumerateUsers(self):
        # any given salesforce instance may start with
        # objects that fullfill the basic enumerateUsers 
        # criteria.  This becomes our offset for calls 
        # to enumerateUsers w/ no id or login
        return_offset = len(self.userenumerator.enumerateUsers())
        
        count = 10 
        
        for x in range(count):
            username = '%s_user_%i' % (self.username, x)
            obj = dict(type=SF_TEST_OBJECT_TYPE,
                LastName=username,
                UserName__c=username,
                Password__c=self.password,
            )
            
            # XXX this is unnecessary, let's save
            # the api calls and create these in bulk
            res = self.toolbox.create(obj)
            # add our user to the _toCleanUp list for removal via the 
            # salesforce api regardless of success/failure
            sfUserId = res[0]['id']
            self._toCleanUp.append(sfUserId)
        
        ret = self.userenumerator.enumerateUsers()
        self.assertEqual(len(ret), count + return_offset)
        
        ret = self.userenumerator.enumerateUsers(id='%s_user_1' % self.username, exact_match=True)
        self.assertEqual(len(ret), 1)              
        
        # make sure required keys are returned
        for k in ('id', 'login', 'pluginid'):
            self.failUnless(k in ret[0].keys())
        
        ret = self.userenumerator.enumerateUsers(login='%s_user_1' % self.username, exact_match=True)
        self.assertEqual(len(ret), 1)
        
        # searching multiple ids
        ret = self.userenumerator.enumerateUsers(id=('%s_user_1' % self.username, '%s_user_2' % self.username), exact_match=True )
        self.assertEqual(len(ret), 2)

        # searching multiple logins, sorted by id
        ret = self.userenumerator.enumerateUsers(login=('%s_user_2' % self.username, '%s_user_1' % self.username), exact_match=True, sort_by='id' )
        self.assertEqual(len(ret), 2)
        self.failUnless(ret[0]['id'].endswith('1'))
        self.failUnless(ret[1]['id'].endswith('2'))
        
        # non-exact search
        ret = self.userenumerator.enumerateUsers(id='user_1', exact_match=False)
        self.assertEqual(len(ret), 1)
        
        # can limit using max_results
        ret = self.userenumerator.enumerateUsers(max_results=5)
        self.assertEqual(len(ret), 5)
        
        ret = self.userenumerator.enumerateUsers(max_results=20)
        if return_offset + len(ret) <= 20:
            self.assertEqual(len(ret), count + return_offset)
        else:
            self.assertEqual(len(ret), 20)
    
    def testEnumerationAccountsForCustomSOQLCondition(self):
        """Ensure that user enumeration accounts for an
           extra auth condition clause
        """
        # the extra condition we're going to use to "protect" authentication
        soqlClause = """Email like '%@example.com'"""
        
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.username,
            UserName__c = self.username,
            Password__c = self.password,
        )
        # create our user as above
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # a user search should return our newly availble user
        self.assertEqual(len(self.userenumerator.enumerateUsers(login=self.username, exact_match=True)), 1)
        
        # set custom SOQL condition
        self.userenumerator.setAuthConditionClause(soqlClause)
        
        # and with that, a search no longer turns up any results
        self.assertEqual(len(self.userenumerator.enumerateUsers(login=self.username, exact_match=True)), 0)

    def testEnumerationForFullnameKeywordArg(self):
        """Ensure that when a search is performed against the 'fullname' keyword,
           no items are returned if there is no mapping for this field.
        """
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.username,
            UserName__c = self.username,
            Password__c = self.password,
        )
        # create our user as above
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        keywords = {'fullname': self.username}

        # a user search with a 'fullname' search term should return our user and only our user. 
        # 'fullname' is not mapped to any salesforce field, but we'll fall back to searching id/login
        # fields if they exist, and find a match there.
        self.assertEqual(1, len(self.userenumerator.enumerateUsers(exact_match=False, **keywords)))
        
        # A 'fullname' search term that matches no usernames or id's should return no results at all
        keywords['fullname'] = 'obscure name belonging to no one'
        self.assertEqual(0, len(self.userenumerator.enumerateUsers(exact_match=False, **keywords)))

    def testEnumerationWithFullnameMappedToSFField(self):
        # reset our property mapping so we include 'fullname' as a local name
        prop_config_mapping = {
            'fullname':'LastName',
        }
        target = 'McFullname'
        self.plugin.setLocalToSFMapping(prop_config_mapping, mapType='properties')
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = target,
            UserName__c = self.username,
            Password__c = self.password,
        )
        # create our user as above
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        keywords = {'fullname':target}
        self.assertEqual(1, len(self.userenumerator.enumerateUsers(exact_match=False, **keywords)))
    
    def testBuildEnumerationQuery(self):
        # an empty query should result in an empty where clause...
        whereClause = self.userenumerator._buildEnumerationQuery('')
        self.failIf(whereClause)
        
        # ...unless there's an auth condition clause
        self.userenumerator.setAuthConditionClause("LastName!='foo'")
        whereClause = self.userenumerator._buildEnumerationQuery('')
        self.assertEqual(whereClause, "LastName!='foo'")
        
        # if there's an auth clause AND an extra query, they should be concatenated
        whereClause = self.userenumerator._buildEnumerationQuery("FirstName!='bar'")
        self.assertEqual(whereClause, "FirstName!='bar' and LastName!='foo'")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserEnumerationPlugin))
    return suite
