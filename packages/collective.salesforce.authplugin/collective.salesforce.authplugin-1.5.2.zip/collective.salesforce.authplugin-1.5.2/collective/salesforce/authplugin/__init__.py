# Zope
from AccessControl.Permissions import add_user_folders

# PAS
from Products.PluggableAuthService.PluggableAuthService import \
        registerMultiPlugin

# PLUGINS

# user multi plugin
from plugins.sfausermanager import manage_addSalesforceAuthMultiPlugin
from plugins.sfausermanager import SalesforceAuthMultiPlugin, \
    salesforceAuthMultiPluginAddForm

registerMultiPlugin(SalesforceAuthMultiPlugin.meta_type)

def initialize(context):
    context.registerClass(SalesforceAuthMultiPlugin,
            permission = add_user_folders,
            constructors = (salesforceAuthMultiPluginAddForm,
                    manage_addSalesforceAuthMultiPlugin ),
            visibility = None,
            icon='www/salesforce.gif'
            )
