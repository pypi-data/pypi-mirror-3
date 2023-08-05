from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager
from Acquisition import aq_base

# supported plugin interfaces
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin, \
    IUserAdderPlugin, IUserEnumerationPlugin, IPropertiesPlugin
from Products.PlonePAS.interfaces.plugins import IUserManagement
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN, CACHEHANDLER

from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO

def addCacheHandlers(portal, out):
    """ Add RAM cache handlers """
    print >>out, "Adding cache handler %s" % CACHEHANDLER
    mgrs = [(RAMCacheManager, CACHEHANDLER),]
    for mgr_class, mgr_id in mgrs:
        existing = portal._getOb(mgr_id, None)
        if existing is None:
            portal._setObject(mgr_id, mgr_class(mgr_id))
        else:
            unwrapped = aq_base(existing)
            if not isinstance(unwrapped, mgr_class):
                portal._delObject(mgr_id)
                portal._setObject(mgr_id, mgr_class(mgr_id))

def addCacheForAuthPlugin(portal, out, plugin=AUTHMULTIPLUGIN):
    ram_cache_id = CACHEHANDLER
    if ram_cache_id in portal.objectIds():
        cache = getattr(portal, ram_cache_id)
        settings = cache.getSettings()
        settings['max_age'] = 10*60 # keep for up to 10 minutes
        cache.manage_editProps('Cache for Salesforce Auth Plugin queries to Salesforce.com', settings)
    plugin = getattr(portal.acl_users, plugin, None)
    if plugin is not None and getattr(aq_base(plugin), 'ZCacheable_setManagerId', None) is not None:
        plugin.ZCacheable_setManagerId(ram_cache_id)
        plugin.ZCacheable_setEnabled(1)
    


def createSalesforceAuthMultiPlugin(portal, out, id=AUTHMULTIPLUGIN, title='Salesforce Auth Multi Plugin'):
    print >>out, "Adding a %s" % id
    acl=getToolByName(portal, "acl_users")
    if not id in acl.objectIds():
        acl.manage_addProduct[PROJECTNAME].manage_addSalesforceAuthMultiPlugin(
                id=id, 
                title=title,)
        print >>out, "added %s" % id
    else:
        print >>out, "%s already found in acl_users", id

def activatePlugin(portal, out, plugin):
    """Utility to activate plugins by their id
       and the desired pas interface to be activated.
    """
    acl=getToolByName(portal, "acl_users")
    plugin=getattr(acl, plugin)
    
    activate=[]
    
    for info in acl.plugins.listPluginTypeInfo():
        interface=info["interface"]
        interface_name=info["id"]
        if plugin.testImplements(interface):
            activate.append(interface_name)
            print >>out, "Activating interface %s for plugin %s" % \
                    (interface_name, info["title"])
    
    plugin.manage_activateInterfaces(activate)

def movePluginsUp(portal, out, plugin_type, ids_to_move):
    """Outsource work to the plugin registry
    """
    acl=getToolByName(portal, "acl_users")
    while acl.plugins.listPlugins(plugin_type)[0][0] != ids_to_move:
        acl.plugins.movePluginsUp(plugin_type, [ids_to_move,])

def install(self, out=None, plugin_id=AUTHMULTIPLUGIN, plugin_title='Salesforce Auth Multi Plugin'):
    out = StringIO()
    # active and move up our authentication plugin
    createSalesforceAuthMultiPlugin(self, out, id=plugin_id, title=plugin_title)
    activatePlugin(self, out, plugin_id,)
    
    for ifaces in (
            ('IAuthenticationPlugin', IAuthenticationPlugin),
            ('IUserAdderPlugin', IUserAdderPlugin),
            ('IPropertiesPlugin', IPropertiesPlugin),
            ('IUserEnumerationPlugin', IUserEnumerationPlugin),
            ('IUserManagement', IUserManagement),
        ):
        movePluginsUp(self, out, ifaces[1], plugin_id,)
    
    addCacheHandlers(self, out)
    addCacheForAuthPlugin(self, out, plugin=plugin_id)
    
def uninstall(self, reinstall=False):
    if not reinstall:
        out = StringIO()
                                   
        acl=getToolByName(self, "acl_users")
        if AUTHMULTIPLUGIN in acl.objectIds():
            acl.manage_delObjects(ids=[AUTHMULTIPLUGIN,])
            print >>out, "Removing %s" % AUTHMULTIPLUGIN
