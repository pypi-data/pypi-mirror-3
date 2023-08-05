GLOBALS = globals()

PROJECTNAME = 'collective.salesforce.authplugin'

# plugin names
AUTHMULTIPLUGIN  = 'salesforceauthmultiplugin'

# test configuration options
SF_TEST_OBJECT_TYPE = 'Contact'

# Cache result of authentication?
# This may speed things up, but at the expense of a delay in picking up changed passwords
# from Salesforce (depending upon your cache settings).
CACHE_PASSWORDS = False

# Id used for the Salesforce Auth Plugin Cache Handler
CACHEHANDLER = "SalesforceAuthPluginCache"