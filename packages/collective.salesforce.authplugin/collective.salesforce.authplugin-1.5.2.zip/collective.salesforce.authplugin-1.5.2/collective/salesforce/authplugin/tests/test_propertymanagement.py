import sys
from beatbox import SoapFaultError
from datetime import date

from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import AUTHMULTIPLUGIN, SF_TEST_OBJECT_TYPE
from Products.PlonePAS.sheet import MutablePropertySheet
from DateTime import DateTime

class TestUserManagmentPlugin(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        # disable the cache for tests in TestUserManagmentPlugin
        self.plugin.ZCacheable_setManagerId(None)
        
        self.acl = self.portal.acl_users
        self.plugins = self.acl.plugins
        self.propertymgmt = getattr(self.acl, AUTHMULTIPLUGIN)
        self.membership = self.portal.portal_membership
        
        self.username = 'plonetestcase'
        self.lastname = 'McPlonesonProp'
        self.password = 'password'
        self.assistant_name = "Radar O'Reilly"
        self.department = "Web Developers"
        self.changed_assistant_name = "Mary Tyler Moore"
        self.changed_department = "Administration"
    
    def testGetPropertiesForUser(self):
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            AssistantName = self.assistant_name,
            Department = self.department,
        )
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # ensure the member data and property sheet data is correct
        mem = self.membership.getMemberById(self.username)
        self.failUnless(mem)
        
        self.failUnless('salesforceauthmultiplugin' in mem.listPropertysheets())
        
        ps = mem.getPropertysheet(AUTHMULTIPLUGIN)
        self.failUnless(ps)
        
        self.failUnless(ps.hasProperty('assistant_name'))
        self.assertEqual('string', ps.propertyInfo('assistant_name')['type'])
        self.assertEqual(self.assistant_name, mem.getProperty('assistant_name'))
        self.assertEqual(self.department, mem.getProperty('department'))
    
    def testDateTimeGetPropertiesForUser(self):
        dt_time = DateTime("2006/08/05" + ' GMT+0')
        
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            Birthdate = DateTime("2006/08/05" + ' GMT+0').HTML4(),
        )
        
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # update our properties to manage birtdate
        # prop mapping
        prop_config_mapping = {
            'birthdate':'Birthdate',
        }
        self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')
        
        # ensure the member data and property sheet data is correct
        mem = self.membership.getMemberById(self.username)
        self.failUnless(mem)
        
        self.failUnless('salesforceauthmultiplugin' in mem.listPropertysheets())
        
        ps = mem.getPropertysheet(AUTHMULTIPLUGIN)
        self.failUnless(ps)
        
        # check birthdate
        self.failUnless(ps.hasProperty('birthdate'))
        self.assertEqual('date', ps.propertyInfo('birthdate')['type'])
        self.assertEqual(dt_time.earliestTime().parts()[:3], mem.getProperty('birthdate').parts()[:3])
    
    def testNullValueGetPropertiesForUser(self):
        # create user
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
        )
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        prop_config_mapping = {
            'birthdate':'Birthdate',
        }
        self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')
        
        # ensure the member data and property sheet data is correct
        mem = self.membership.getMemberById(self.username)
        self.failUnless(mem)
        
        self.failUnless('salesforceauthmultiplugin' in mem.listPropertysheets())
        ps = mem.getPropertysheet(AUTHMULTIPLUGIN)
        self.failUnless(ps)
        self.failUnless(ps.hasProperty('birthdate'))
        # for now, field type falls back to string if Salesforce returned null value
        self.assertEqual('string', ps.propertyInfo('birthdate')['type'])
        self.assertEqual('', mem.getProperty('birthdate'))
    
    def testOnValueWorksAsString(self):
        """The Plone UI passes the string 'on' for boolean fields represented by a
           HTML checkbox input. Since we sniff for this value and convert it to a python
           boolean (True) before passing it to Salesforce, we need to make sure we don't 
           erroneously convert the value 'on' when it's passed in from a string field.
        """
        # User dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = 'on',
            UserName__c = self.username,
            Password__c = self.password,
        )
        # update our properties to manage our odd test
        # prop mapping.
        prop_config_mapping = {
            'on_or_off':'LastName',
        }
        self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')        

        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # ensure the member data and property sheet data is correct
        mem = self.membership.getMemberById(self.username)
        self.failUnless(mem)
        
        self.failUnless('salesforceauthmultiplugin' in mem.listPropertysheets())
        
        ps = mem.getPropertysheet(AUTHMULTIPLUGIN)
        self.failUnless(ps)
        
        # check 'on_or_off' for value 'on'
        self.failUnless(ps.hasProperty('on_or_off'))
        self.assertEqual('string', ps.propertyInfo('on_or_off')['type'])
        self.assertEqual('on', mem.getProperty('on_or_off'))
    
    def testBooleanGetPropertiesForUser(self):
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            Favorite_Boolean__c = True,
        )
        try:
            # create our user
            res = self.toolbox.create(obj)
            # add our user to the _toCleanUp list for removal via the 
            # salesforce api regardless of success/failure
            sfUserId = res[0]['id']
            self._toCleanUp.append(sfUserId)
            
            # update our properties to manage favorite boolean
            # prop mapping
            prop_config_mapping = {
                'favorite_boolean':'Favorite_Boolean__c',
            }
            self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')
            
            # ensure the member data and property sheet data is correct
            mem = self.membership.getMemberById(self.username)
            self.failUnless(mem)
            
            self.failUnless('salesforceauthmultiplugin' in mem.listPropertysheets())
            
            ps = mem.getPropertysheet(AUTHMULTIPLUGIN)
            self.failUnless(ps)
            
            # check favorite boolean
            self.failUnless(ps.hasProperty('favorite_boolean'))
            self.assertEqual('boolean', ps.propertyInfo('favorite_boolean')['type'])
            self.assertEqual(True, mem.getProperty('favorite_boolean'))
        except SoapFaultError:
            print >> sys.stderr, ("WARNING: For this test to successfully run, you need to add the following custom fields"
                                  " to the Contact object: Favorite_Boolean__c.  See README.txt --> 'Running Tests' "
                                  "for more.")
    
    def testFloatGetPropertiesForUser(self):
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            Favorite_Float__c = 12.2,
        )
        
        try:
            # create our user
            res = self.toolbox.create(obj)
            # add our user to the _toCleanUp list for removal via the 
            # salesforce api regardless of success/failure
            sfUserId = res[0]['id']
            self._toCleanUp.append(sfUserId)
            
            # update our properties to manage float
            # prop mapping
            prop_config_mapping = {
              'favorite_float':'Favorite_Float__c',
            }
            self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')
            
            # ensure the member data and property sheet data is correct
            mem = self.membership.getMemberById(self.username)
            self.failUnless(mem)
            
            self.failUnless('salesforceauthmultiplugin' in mem.listPropertysheets())
            
            ps = mem.getPropertysheet(AUTHMULTIPLUGIN)
            self.failUnless(ps)
            
            # check favorite boolean
            self.failUnless(ps.hasProperty('favorite_float'))
            self.assertEqual('float', ps.propertyInfo('favorite_float')['type'])
            self.assertEqual(12.2, mem.getProperty('favorite_float'))
        
        except SoapFaultError:
            print >> sys.stderr, ("WARNING: For this test to successfully run, you need to add the following custom fields"
                                " to the Contact object: Favorite_Float__c. See README.txt --> 'Running Tests' "
                                  "for more.")
    
    def testGetPropertiesReturnsEmptyPropSheetWhenNoPropertyMapping(self):
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            AssistantName = self.assistant_name,
            Department = self.department,
        )
        
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # clear out our mapping
        self.propertymgmt.setLocalToSFMapping({})
        
        # ensure a configuration error is raised when we're operating as an 
        # IPropertyPlugin without any property mapping
        # self.assertRaises(ConfigurationError, self.membership.getMemberById, self.username)
        mem = self.membership.getMemberById(self.username)
        ps = mem.getPropertysheet(AUTHMULTIPLUGIN)
        self.failUnless(ps)
        self.failIf(ps.propertyIds())
    
    def testSetPropertiesForUser(self):
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            AssistantName = self.assistant_name,
            Department = self.department,
        )
        
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        mem = self.membership.getMemberById(self.username)
        info = {
            'assistant_name': self.changed_assistant_name,
            'department': self.changed_department,
        }
        
        ps = MutablePropertySheet(self.username, **info)
        self.propertymgmt.setPropertiesForUser(user=mem, propertysheet=ps)
        
        memUpdated = self.membership.getMemberById(self.username)
        ps = memUpdated.getPropertysheet(AUTHMULTIPLUGIN)
        
        self.failUnless(ps.hasProperty('assistant_name'))
        self.assertEqual('string', ps.propertyInfo('assistant_name')['type'])
        self.assertEqual(self.changed_assistant_name, memUpdated.getProperty('assistant_name'))
        self.assertEqual(self.changed_department, memUpdated.getProperty('department'))        
    
    def testDateTimeSetPropertiesForUser(self):
        dt_time = date(2006, 8, 5)
        
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            Birthdate = dt_time,
        )
        
        # update our properties to manage birtdate prop mapping
        prop_config_mapping = {
            'birthdate':'Birthdate',
        }
        self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')
        
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # ensure the member data and property sheet data is correct
        mem = self.membership.getMemberById(self.username)
        chgd_time = DateTime()
        info = {
            'birthdate': chgd_time,
        }
        
        ps = MutablePropertySheet(self.username, **info)
        self.propertymgmt.setPropertiesForUser(user=mem, propertysheet=ps)
        
        memUpdated = self.membership.getMemberById(self.username)
        ps = memUpdated.getPropertysheet(AUTHMULTIPLUGIN)
        
        self.failUnless(ps.hasProperty('birthdate'))
        self.assertEqual('date', ps.propertyInfo('birthdate')['type'])
        # we're dealing with a birthday here, so we just care about the YYYY/MM/DD
        self.assertEqual(chgd_time.earliestTime().parts()[:3], memUpdated.getProperty('birthdate').parts()[:3])
    
    def testBooleanSetPropertiesForUser(self):
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = self.lastname,
            UserName__c = self.username,
            Password__c = self.password,
            Favorite_Boolean__c = False,
        )
        
        # update our properties to manage birtdate prop mapping
        prop_config_mapping = {
            'favorite_boolean':'Favorite_Boolean__c',
        }
        self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')
        
        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)
        
        # ensure the member data and property sheet data is correct
        mem = self.membership.getMemberById(self.username)
        info = {
            'favorite_boolean': 'on',
        }
        
        ps = MutablePropertySheet(self.username, **info)
        self.propertymgmt.setPropertiesForUser(user=mem, propertysheet=ps)
        
        memUpdated = self.membership.getMemberById(self.username)
        ps = memUpdated.getPropertysheet(AUTHMULTIPLUGIN)
        
        self.failUnless(ps.hasProperty('favorite_boolean'))
        self.assertEqual('boolean', ps.propertyInfo('favorite_boolean')['type'])
        self.assertEqual(True, memUpdated.getProperty('favorite_boolean'))
    
    def testOnValueSetPropertiesForUser(self):
        """The Plone UI passes the string 'on' for boolean fields represented by a
           HTML checkbox input. Since we sniff for this value and convert it to a python
           boolean (True) before passing it to Salesforce, we need to make sure we don't 
           erroneously convert the value 'on' when it's passed in from a string field.
           Since 'LastName' is a string field in Salesforce, we should not convert to 
           a boolean.
        """
        # user dictionary
        obj = dict(type = SF_TEST_OBJECT_TYPE,
            LastName = 'off',
            UserName__c = self.username,
            Password__c = self.password,
        )
        
        # update our properties to manage birtdate prop mapping
        prop_config_mapping = {
            'on_or_off':'LastName',
        }
        self.propertymgmt.setLocalToSFMapping(prop_config_mapping, mapType='properties')

        # create our user
        res = self.toolbox.create(obj)
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = res[0]['id']
        self._toCleanUp.append(sfUserId)

        # ensure the member data and property sheet data is correct
        mem = self.membership.getMemberById(self.username)
        info = {
            'on_or_off': 'on',
        }

        ps = MutablePropertySheet(self.username, **info)
        self.propertymgmt.setPropertiesForUser(user=mem, propertysheet=ps)

        memUpdated = self.membership.getMemberById(self.username)
        ps = memUpdated.getPropertysheet(AUTHMULTIPLUGIN)

        self.failUnless(ps.hasProperty('on_or_off'))
        self.assertEqual('string', ps.propertyInfo('on_or_off')['type'], "Should be a string! Is it a boolean??")
        self.assertEqual('on', memUpdated.getProperty('on_or_off'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserManagmentPlugin))
    return suite
