import sha
from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin import config

from Products.PluggableAuthService.utils import createViewName

CACHE_MANAGER_ID = config.CACHEHANDLER
_marker = []

class CacheTestCase(SalesforceAuthPluginTestCase):
    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        # disable the cache for test cases using CacheTestCase
        self.plugin.ZCacheable_setManagerId(None)
        
        self.plugin = getattr(self.portal.acl_users.plugins, config.AUTHMULTIPLUGIN)
        self.plugin.ZCacheable_setManagerId(CACHE_MANAGER_ID)
        self.username = 'user1'
        self.password = 'pass1'
        self.plugin.doAddUser(self.username, self.password)
        soql = "SELECT UserName__c, Id FROM %s WHERE UserName__c='%s'" % (
            config.SF_TEST_OBJECT_TYPE,
            self.username
            )
        user_list = self.toolbox.query(soql)
        sfUserId = user_list['records'][0]['Id']
        self._toCleanUp.append(sfUserId)
        
    def assertEmptyCache(self, view_name=None, keywords={}):
        if view_name is None and hasattr(self, 'view_name'):
            view_name = self.view_name
        self.failUnless(self.plugin.ZCacheable_get(view_name = view_name, keywords = keywords, default = _marker) is _marker,
            '%s cache is not empty' % view_name)
        
    def assertNotEmptyCache(self, view_name=None, keywords={}):
        if view_name is None and hasattr(self, 'view_name'):
            view_name = self.view_name
        self.failIf(self.plugin.ZCacheable_get(view_name = view_name, keywords = keywords, default = _marker) is _marker,
            '%s cache is empty' % view_name)
    
    def tearDown(self):
        SalesforceAuthPluginTestCase.tearDown(self)
        self.plugin.ZCacheable_setManagerId(None)
    

class TestAuthenticateCredentialsCaching(CacheTestCase):
    def testIsCacheEnabled(self):
        self.failUnless(self.plugin.ZCacheable_isCachingEnabled())
    
    def testInitialAuthCacheIsEmpty(self):
        view_name = createViewName('authenticateCredentials', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'password':sha.sha(self.password).hexdigest()},
                default=_marker)
        self.failUnless(user is _marker)
    
    def testAuthIsNotCached(self):
        config.CACHE_PASSWORDS=False
        self.plugin.authenticateCredentials({'login': self.username, 'password': self.password})
        view_name = createViewName('authenticateCredentials', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'password':sha.sha(self.password).hexdigest()},
                default=_marker)
        self.failUnless(user is _marker)
    
    def testAuthIsCachedIfWeSaySo(self):
        config.CACHE_PASSWORDS=True
        self.plugin.authenticateCredentials({'login': self.username, 'password': self.password})
        view_name = createViewName('authenticateCredentials', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'password':sha.sha(self.password).hexdigest()},
                default=_marker)
        self.failUnless(user is not _marker)
    
    def testRemoveUserInvalidatesCache(self):
        print ("""Known issue: salesforceauthplugin doesn't remove users,
            so we can't test cache invalidation on user deletion.""")
        return
        
        config.CACHE_PASSWORDS=True
        
        # Prime our caches
        self.plugin.authenticateCredentials({'login': self.username, 'password': self.password})
        
        # Remove a user should invalidate all her cache entries
        self.plugin.removeUser(self.username)
        
        view_name = createViewName('authenticateCredentials', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'password':sha.sha(self.password).hexdigest()},
                default=_marker)
        self.failUnless(user is _marker)
    
    def testChangePasswordInvalidatesCache(self):
        # Prime our caches
        self.plugin.authenticateCredentials({'login': self.username, 'password': self.password})
        
        # Changing a user's password should invalidate all her cache entries
        self.plugin.doChangeUser(self.username, self.password)
        
        view_name = createViewName('authenticateCredentials', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'password':sha.sha(self.password).hexdigest()},
                default=_marker)
        self.failUnless(user is _marker)
    
    def testCachedCredentialsHashesPasswords(self):
        config.CACHE_PASSWORDS=True
        self.plugin.authenticateCredentials({'login': self.username, 'password': self.password})
        view_name = createViewName('authenticateCredentials', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={}, # intentionally blank, view without password hash not cached
                default=_marker)
        self.failUnless(user is _marker)
        self.failIf(self.plugin.authenticateCredentials({'login': self.username, 'password': 'secret'}))
        
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'password':sha.sha(self.password).hexdigest()},
                default=_marker)
        self.failIf(user is _marker)
    

class TestUserPropertiesCaching(CacheTestCase):
    def testIsCacheEnabled(self):
        self.failUnless(self.plugin.ZCacheable_isCachingEnabled())

    def testInitialPropertyCacheIsEmpty(self):
        view_name = createViewName('getPropertiesForUser', self.username)
        props = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'plugin_id': self.plugin.getId()},
                default=_marker)
        self.failUnless(props is _marker)

    def testGetPropertiesForUserIsCached(self):
        user = self.portal.portal_membership.getMemberById(self.username)
        self.plugin.getPropertiesForUser(user)
        view_name = createViewName('getPropertiesForUser', self.username)
        props = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'plugin_id': self.plugin.getId()},
                default=_marker)
        self.failUnless(props is not _marker)
        
    def test_dataTypeForSFField(self):
        self.plugin._dataTypeForSFField('Contact', 'LastName')
        view_name = createViewName('_dataTypeForSFField-Contact-LastName')
        props = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={},
                default=_marker)
        self.failIf(props is _marker)

    def testUpdateUserInfoInvalidatesCache(self):
        # Prime our caches
        user = self.portal.portal_membership.getMemberById(self.username)
        self.plugin.getPropertiesForUser(user)

        # Setting a property should invalidate the cache
        self.plugin.updateUserInfo(user, None, {})

        view_name = createViewName('getPropertiesForUser', self.username)
        props = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'plugin_id': self.plugin.getId()},
                default=_marker)
        self.failUnless(props is _marker)

    def testSetPropertiesForUserInvalidatesCache(self):
        # Prime our caches
        user = self.portal.portal_membership.getMemberById(self.username)
        self.plugin.getPropertiesForUser(user)

        # Setting a property should invalidate the cache
        from Products.PlonePAS.sheet import MutablePropertySheet
        self.plugin.setPropertiesForUser(user, MutablePropertySheet('test'))

        view_name = createViewName('getPropertiesForUser', self.username)
        props = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords={'plugin_id': self.plugin.getId()},
                default=_marker)
        self.failUnless(props is _marker)

class TestEnumerateUsersCaching(CacheTestCase):
    def testIsCacheEnabled(self):
        self.failUnless(self.plugin.ZCacheable_isCachingEnabled())

    def testInitialPropertyCacheIsEmpty(self):
        view_name = createViewName('enumerateUsers')
        info = {
            'plugin_id': self.plugin.getId(),
            'id_or_login': (),
            'exact_match': False,
            'sort_by': None,
            'max_results': None,
        }
        users = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        self.failUnless(users is _marker)
        
    def testUserEnumerationIsCached(self):
        # prime the cache
        self.plugin.enumerateUsers(id=self.username)
        
        view_name = createViewName('enumerateUsers')
        info = {
            'plugin_id': self.plugin.getId(),
            'id_or_login': (self.username,),
            'exact_match': False,
            'sort_by': None,
            'max_results': None,
        }
        users = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        self.failIf(users is _marker)
        
    def testCachingBasedOnKeywords(self):
        # prime cache (with user)
        self.plugin.enumerateUsers(id=self.username)
        
        # prime cache (non-existent user)
        self.plugin.enumerateUsers(id='foobar')
        
        # make sure the cache entries are distinct
        view_name = createViewName('enumerateUsers')
        info = {
            'plugin_id': self.plugin.getId(),
            'id_or_login': (self.username,),
            'exact_match': False,
            'sort_by': None,
            'max_results': None,
        }
        users1 = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        info['id'] = ['foobar']
        users2 = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        self.assertNotEqual(users1, users2)

    def testDoAddUserInvalidatesCache(self):
        # prime cache
        self.plugin.enumerateUsers()
        
        # add user (use the user adder test helper, to avoid leaving cruft in Salesforce)
        from collective.salesforce.authplugin.tests.test_useradder import add_user_in_test
        add_user_in_test(self, 'Cache Test User', 'password')
        
        # make sure the cache is empty
        view_name = createViewName('enumerateUsers')
        info = {
            'plugin_id': self.plugin.getId(),
            'id_or_login': (),
            'exact_match': False,
            'sort_by': None,
            'max_results': None,
        }
        users = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        self.failUnless(users is _marker)
        
    def testRemoveUserInvalidatesCache(self):
        print ("""Known issue: salesforceauthplugin doesn't remove users,
            so we can't test cache invalidation on user deletion.""")
        return
        
        # prime the cache
        self.plugin.enumerateUsers()
        
        # remove the user
        self.plugin.removeUser(self.username)
        
        view_name = createViewName('enumerateUsers')
        info = {
            'plugin_id': self.plugin.getId(),
            'id_or_login': (),
            'exact_match': False,
            'sort_by': None,
            'max_results': None,
        }
        users = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        self.failUnless(users is _marker)
        
    def testAllowPasswordSetUsesUserEnumerationCacheIfAvailable(self):
        """ Plone's user listing first calls enumerateUsers and then calls canPasswordSet
            on each user.  We optimize for this scenario by using the cached enumerateUsers
            results if available, rather than a new query.  Let's make sure that this returns
            the same result.
        """
        
        # make sure uncached result is as expected
        self.failUnless(self.plugin.allowPasswordSet(self.username))
        
        # make sure cache is initially empty
        view_name = createViewName('enumerateUsers')
        info = {
            'plugin_id': self.plugin.getId(),
            'id_or_login': (),
            'exact_match': False,
            'sort_by': None,
            'max_results': None,
        }
        users = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        self.failUnless(users is _marker)
        
        # prime the cache
        self.plugin.enumerateUsers()
        
        # make sure cache is primed
        users = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=info,
                default=_marker)
        self.failIf(users is _marker)
        
        # make sure cached result is as expected
        self.failUnless(self.plugin.allowPasswordSet(self.username))
        
class TestInvalidationOnToolConfiguration(CacheTestCase):
    
    def afterSetUp(self):
        CacheTestCase.afterSetUp(self)
        
        self.cache_info = {
            'authenticateCredentials': {
                'view_name': createViewName('authenticateCredentials', self.username),
                'keywords': {
                    'password':sha.sha(self.password).hexdigest(),
                    }
                },
            'getPropertiesForUser': {
                'view_name': createViewName('getPropertiesForUser', self.username),
                'keywords': { 'plugin_id': self.plugin.getId() },
                },
            'enumerateUsers': {
                'view_name': createViewName('enumerateUsers'),
                'keywords': {
                    'plugin_id': self.plugin.getId(),
                    'id_or_login': (self.username,),
                    'exact_match': False,
                    'sort_by': None,
                    'max_results': None,
                    }
                }
            }
        
        # prime all the caches
        config.CACHE_PASSWORDS=True
        self.plugin.authenticateCredentials({'login': self.username, 'password': self.password})
        self.assertNotEmptyCache('authenticateCredentials')
        
        user = self.portal.portal_membership.getMemberById(self.username)
        self.plugin.getPropertiesForUser(user)
        self.assertNotEmptyCache('getPropertiesForUser')
        
        self.plugin.enumerateUsers(id=self.username)
        self.assertNotEmptyCache('enumerateUsers')
        
    def assertEmptyCache(self, cache_name):
        CacheTestCase.assertEmptyCache(self, **self.cache_info[cache_name])
        
    def assertNotEmptyCache(self, cache_name):
        CacheTestCase.assertNotEmptyCache(self, **self.cache_info[cache_name])
                
    def testAllCachesClearedOnSetSFObjectType(self):
        self.plugin.setSFObjectType('Lead')
        self.assertEmptyCache('authenticateCredentials')
        self.assertEmptyCache('getPropertiesForUser')
        self.assertEmptyCache('enumerateUsers')
        
    def testAuthCacheClearedOnSetAuthConditionClause(self):
        self.plugin.setAuthConditionClause('')
        self.assertEmptyCache('authenticateCredentials')
        
    def testAuthCacheClearedOnSetEncryptionAlgorithm(self):
        self.plugin.setEncryptionAlgorithm('plain')
        self.assertEmptyCache('authenticateCredentials')
        
    def testPropertiesCacheClearedOnSetLocalToSFMapping(self):
        self.plugin.setLocalToSFMapping({})
        self.assertEmptyCache('getPropertiesForUser')
            
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAuthenticateCredentialsCaching))
    suite.addTest(makeSuite(TestUserPropertiesCaching))
    suite.addTest(makeSuite(TestEnumerateUsersCaching))
    suite.addTest(makeSuite(TestInvalidationOnToolConfiguration))
    return suite
