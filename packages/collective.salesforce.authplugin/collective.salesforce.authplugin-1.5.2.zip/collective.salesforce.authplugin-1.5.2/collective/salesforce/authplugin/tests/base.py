"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase
from Products.Five import zcml
from Products.Five import fiveconfigure

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct('PluggableAuthService')
ZopeTestCase.installProduct('salesforcebaseconnector')
ZopeTestCase.installProduct('StandardCacheManagers')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase, FunctionalTestCase
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.PloneTestCase import setupPloneSite

from Products.salesforcebaseconnector.tests.layer import SalesforcePloneLayer

# Local imports
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN

@onsetup
def setup_collective_salesforce_auth():
    """Set up the additional products required for the collective.salesforce.authplugin.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the collective.salesforce.authplugin package.
    
    fiveconfigure.debug_mode = True
    import collective.salesforce.authplugin
    zcml.load_config('configure.zcml', collective.salesforce.authplugin)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    ZopeTestCase.installPackage('collective.salesforce.authplugin')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_collective_salesforce_auth()

# **don't install the auth product** here or else 
# test_user_1_ will attempt to be created as a salesforce object
setupPloneSite()

class SalesforceAuthPluginTestCase(PloneTestCase):
    """Base class for integration tests for the 'salesforceauthplugin ' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """
    
    layer = SalesforcePloneLayer
    
    def _configureFieldMappings(self):
        # auth mapping
        auth_config_mapping = {
            'password':'Password__c',
            'username':'UserName__c',
        }
        self.plugin.setLocalToSFMapping(auth_config_mapping, mapType='auth')
        
        # prop mapping
        prop_config_mapping = {
            'assistant_name':'AssistantName',
            'department':'Department',
        }
        self.plugin.setLocalToSFMapping(prop_config_mapping, mapType='properties')
        
    
    def afterSetUp(self):
        """Add the salesforceauthplugin product
        """
        PloneTestCase.afterSetUp(self)
        
        self.toolbox = self.portal.portal_salesforcebaseconnector
        
        # install our product
        self.addProduct(PROJECTNAME)
        
        # configure our plugin for test suite
        self.plugin = getattr(self.portal.acl_users.plugins, AUTHMULTIPLUGIN)
        self._configureFieldMappings()
        
        # for tests, we use 'plain' (= plain text) encryption
        self.plugin.setEncryptionAlgorithm('plain')
        
        # save any objects we create in this List, to be deleted on tearDown        
        self._toCleanUp = []
    
    def tearDown(self):
        if self._toCleanUp:
            # remove all users in bulk via the salesforce api
            self.toolbox.delete(self._toCleanUp)
    

class SalesforceAuthFunctionalTestCase(FunctionalTestCase):
    """Base class for functional tests for the 'salesforceauthplugin ' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

    layer = SalesforcePloneLayer
