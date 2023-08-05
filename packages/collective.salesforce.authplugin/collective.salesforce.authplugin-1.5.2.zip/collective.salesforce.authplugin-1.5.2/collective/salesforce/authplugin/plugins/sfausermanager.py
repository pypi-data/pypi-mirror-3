import os, logging

# Zope
from zope.interface import implements
from zope.component import getAllUtilitiesRegisteredFor
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, package_home
from OFS.Cache import Cacheable
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from beatbox import SoapFaultError

# CMF
from Products.CMFCore.permissions import ManagePortal

# PAS
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.utils import createViewName

# Interfaces & Capabilities
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin, \
    IUserEnumerationPlugin, IUserAdderPlugin, IPropertiesPlugin, IUpdatePlugin
from Products.PlonePAS.interfaces.plugins import IUserManagement, IMutablePropertiesPlugin
from Products.PlonePAS.interfaces.capabilities import IDeleteCapability, IPasswordSetCapability
from collective.salesforce.authplugin.interfaces import IUserManagementPluginPropertyManager, \
    IMappingUI
from collective.salesforce.authplugin.encrypt import IEncrypter    


# Project
from collective.salesforce.authplugin.plugins.base import SalesforceBasePluginMixin
from collective.salesforce.authplugin.mixins import AuthMixin, UserAdderMixin, UserEnumerationMixin, \
    UserManagementMixin, PropertyManagementMixin
from collective.salesforce.authplugin.config import GLOBALS

logger = logging.getLogger("salesforceauthplugin")

_marker = []

_ptdir = os.path.join(package_home(GLOBALS), 'www')

salesforceAuthMultiPluginAddForm= PageTemplateFile(
        'salesforceAuthMultiPluginAddForm', _ptdir)
salesforceAuthMultiPluginEditForm = PageTemplateFile(
        'salesforceAuthMultiPluginEditForm', _ptdir)

sf_obj_type_hints = {}

def manage_addSalesforceAuthMultiPlugin(self, 
    id, title, authConditionClause='', REQUEST=None):
    """ConSalesforceAuthMultiPlugin"""
    self = self.this()
    plugin = SalesforceAuthMultiPlugin(id, title)
    plugin.id = id
    self._setObject(id, plugin)
    plugin = getattr(aq_base(self), id)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/manage_main' % self.absolute_url())

class SalesforceAuthMultiPlugin(SalesforceBasePluginMixin, AuthMixin, 
    UserAdderMixin, UserEnumerationMixin, UserManagementMixin,
    PropertyManagementMixin):
    """Our Salesforce Plugin implementing various PAS and PlonePAS 
       interfaces for user management within a Plone portal.
    """
    implements(IUserManagementPluginPropertyManager, IMappingUI)
    
    security = ClassSecurityInfo()
    meta_type = 'Salesforce Auth Multi Plugin'
    
    def __init__(self, id, title, object_type='Contact'):
        SalesforceBasePluginMixin.__init__(self, id, title)
        
        # default plugin configuration
        self._authConditionClause = ''
        self._sf_object_type = object_type
        
        # plone--> salesforce property/auth mapping data structures
        self._auth_fieldmapping = {}
        self._user_property_mapping = {}
    
    #
    # ZMI Functionality
    # 
    manage_options = (
            dict(label='Config', action='manage_configForm'),
            ) + BasePlugin.manage_options + Cacheable.manage_options
    
    security.declareProtected(ManagePortal, 'manage_configForm')
    manage_configForm = salesforceAuthMultiPluginEditForm
    
    #
    # IUserManagementPluginPropertyManager
    # 
    security.declareProtected(ManagePortal, 'getSFObjectTypes')
    def getSFObjectTypes(self):
        """See ..interfaces.IUserManagementPluginPropertyManager
        """
        salesforce = getToolByName(self, 'portal_salesforcebaseconnector')
        types = salesforce.describeGlobal()['types']
        return types
    
    security.declareProtected(ManagePortal, 'getSFObjectType')
    def getSFObjectType(self):
        """See ..interfaces.IUserManagementPluginPropertyManager"""
        return self._sf_object_type
    
    security.declareProtected(ManagePortal, 'setSFObjectType')
    def setSFObjectType(self, newSFObjectType):
        """See ..interfaces.IUserManagementPluginPropertyManager"""
        self._sf_object_type = str(newSFObjectType).strip()
        
        # invalidate all caches
        self.ZCacheable_invalidate()
    
    security.declareProtected(ManagePortal, 'getLoginFieldName')
    def getLoginFieldName(self):
        """See ..interfaces.IUserManagementPluginPropertyManager
        """
        if self._auth_fieldmapping.has_key('username'):
            return self._auth_fieldmapping['username']
        
        return
    
    security.declareProtected(ManagePortal, 'getPasswordFieldName')
    def getPasswordFieldName(self):
        """See ..interfaces.IUserManagementPluginPropertyManager
        """
        if self._auth_fieldmapping.has_key('password'):
            return self._auth_fieldmapping['password']
        
        return
    
    security.declareProtected(ManagePortal, 'getAuthConditionClause')
    def getAuthConditionClause(self):
        """See ..interfaces.IUserManagementPluginPropertyManager"""
        return self._authConditionClause
    
    security.declareProtected(ManagePortal, 'setAuthConditionClause')
    def setAuthConditionClause(self, authConditionClause=''):
        """See ..interfaces.IUserManagementPluginPropertyManager"""
        
        connector = getToolByName(self, 'portal_salesforcebaseconnector')
        
        try:
            soql = "SELECT Id FROM %s" % self._sf_object_type
            if authConditionClause:
                soql += ' WHERE %s' % authConditionClause
            connector.query(soql)
            value_ok = True
        except SoapFaultError:
            value_ok = False
        
        if value_ok:
            self._authConditionClause = str(authConditionClause).strip()
        
        # invalidate all caches
        self.ZCacheable_invalidate()
        
        return value_ok
    
    security.declareProtected(ManagePortal, 'getEncryptionAlgorithm')
    def getEncryptionAlgorithm(self):
        """See ..interfaces.IUserManagementPluginPropertyManager.
           If not defined for the instance, this will return the class
           default, which is 'plain'
        """
        return self.default_encryption
    
    security.declareProtected(ManagePortal, 'setEncryptionAlgorithm')
    def setEncryptionAlgorithm(self, algorithm='md5'):
        """See ..interfaces.IUserManagementPluginPropertyManager."""
        algorithm = algorithm.strip()
        if algorithm in self.listValidEncryptionAlgorithms():
            self.default_encryption = algorithm
            
            # invalidate all caches
            self.ZCacheable_invalidate()
            
            return True
        else:
            return False
    
    security.declareProtected(ManagePortal, 'listValidEncryptionAlgorithms')
    def listValidEncryptionAlgorithms(self):
        validEncrypters = [encrypter.name for encrypter in getAllUtilitiesRegisteredFor(IEncrypter)]
        
        return validEncrypters
    
    security.declareProtected(ManagePortal, 'manage_updateConf')
    def manage_updateConf(self, SFObjectType='', authConditionClause='', 
                          localToSFAuthMapping=[], localToSFFieldMapping=[], 
                          encryption='md5', REQUEST=None):
        """ Update the config through the ZMI"""
        # update our SFObjectType
        self.setSFObjectType(SFObjectType)
        
        # update our auth and property field mappings
        self.setMappingFromUI(localToSFAuthMapping, 'auth')
        self.setMappingFromUI(localToSFFieldMapping)
        
        if encryption in self.listValidEncryptionAlgorithms():
            self.setEncryptionAlgorithm(encryption)
        
        auth_condition_ok = self.setAuthConditionClause(authConditionClause)
        if auth_condition_ok:
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('%s/manage_configForm?portal_status_message=%s' % (self.absolute_url(),
                    "%s configuration options updated." % self.id))
        else:
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('%s/manage_configForm?portal_status_message=%s' % (self.absolute_url(),
                    "ERROR: The additional soql auth query isn't valid. Reverting back to previous value. Other"
                    " configuration modifications saved."))
    
    #
    # IMappingUI Implementation
    # 
    security.declareProtected(ManagePortal, 'getLocalToSFMapping')
    def getLocalToSFMapping(self, mapType='properties'):
        """See ..interfaces.IMappingUI
        """
        if mapType and mapType=='auth':
            return self._auth_fieldmapping
            
        return self._user_property_mapping
    
    security.declareProtected(ManagePortal, 'setLocalToSFMapping')
    def setLocalToSFMapping(self, dictionary, mapType='properties'):
        """See ..interfaces.IMappingUI
        """
        if mapType=='auth':
            self._auth_fieldmapping = dictionary
        else:
            self._user_property_mapping = dictionary
            
        # invalidate all caches
        self.ZCacheable_invalidate()
    
    security.declareProtected(ManagePortal, 'setMappingFromUI')
    def setMappingFromUI(self, mappingList, mapType='properties'):
        """See ..interfaces.IMappingUI
        """
        mapping = dict()
        # update with new values
        for mappings in mappingList:
            plone_key, salesforce_key = mappings.split('|', 1)
            mapping[plone_key] = salesforce_key
        
        self.setLocalToSFMapping(mapping, mapType)
    
    security.declareProtected(ManagePortal, 'listMappingForLinesField')
    def listMappingForLinesField(self, mapType='properties'):
        """See ..interfaces.IMappingUI
        """
        mappingValues = ""
        
        if mapType == 'auth':
            auth_map = self.getLocalToSFMapping(mapType='auth')
            mapitems = auth_map.items()
        else:
            prop_map = self.getLocalToSFMapping(mapType='properties')
            mapitems = prop_map.items()
        
        for plone_key, salesforce_key in mapitems:
            mappingValues += "%s|%s\n" % (plone_key, salesforce_key)
        return mappingValues
    
    security.declareProtected(ManagePortal, 'listSalesforceFields')
    def listSalesforceFields(self):
        """See ..interfaces.IMappingUI
        """
        # look at some property/property sheet and return all the values
        return self._user_property_mapping.values()
    
    security.declareProtected(ManagePortal, 'listLocalToSFMappings')
    def listLocalToSFMappings(self):
        """See ..interfaces.IMappingUI
        """
        # look at some property/property sheet and return all the pairs ala (local, Salesforce)
        return self._user_property_mapping.items()
    
    
    #
    # Private methods...
    #
    def _getUserInfo(self, user_id):
        """Return symbolic user for capability checking
        """
        soql = "SELECT %s FROM %s WHERE %s = '%s'" % (
            'Id', self._sf_object_type, self.getLoginFieldName(), user_id)
        res = self._getSFConnection().query(soql)
        
        if res['size'] != 1:
            logger.debug("Found %s users for id: [%s]. Can't return user info..." 
                            % (res['size'], user_id))
            return
        return user_id
    
    def _dataTypeForSFField(self, sfObjectType, sfFieldName):
        """Return a string representing the Salesforce data type
           for a given object type and field.
        """
        view_name = createViewName('_dataTypeForSFField', "%s-%s" % (sfObjectType, sfFieldName))
        cached_info = self.ZCacheable_get(view_name=view_name, default=_marker)
        if cached_info is not _marker:
            return cached_info
        objectDesc = self._getSFConnection().describeSObjects(sfObjectType)[0]
        fieldType = objectDesc.fields[sfFieldName].type
        self.ZCacheable_set(fieldType, view_name=view_name)
        
        return fieldType
    
    def _get_sf_obj_type_hints(self):
        global sf_obj_type_hints
        return sf_obj_type_hints


classImplements(SalesforceAuthMultiPlugin,
                IAuthenticationPlugin,
                IUserAdderPlugin,
                IUserManagement,
                IPropertiesPlugin, 
                IUserEnumerationPlugin,
                IMutablePropertiesPlugin,
                IUpdatePlugin,
                IDeleteCapability,
                IPasswordSetCapability,
                )

InitializeClass(SalesforceAuthMultiPlugin)
