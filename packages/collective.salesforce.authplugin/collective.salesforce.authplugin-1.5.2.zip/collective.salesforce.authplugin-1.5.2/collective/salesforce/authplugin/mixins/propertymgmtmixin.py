from datetime import date
from DateTime import DateTime
import logging
import warnings
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PluggableAuthService.utils import createViewName
from Products.PlonePAS.sheet import MutablePropertySheet
from Products.salesforcebaseconnector.utils import DateTime2datetime

logger = logging.getLogger("salesforceauthplugin")
_marker = []

class PropertyManagementMixin:
    """Implements 
       Products.PluggableAuthService.interfaces.plugins.IPropertiesPlugin
    """
    security = ClassSecurityInfo()
    
    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ See IPropertiesPlugin
        """
        logger.debug('calling getPropertiesForUser')

        # don't try to fetch properties for groups
        if getattr(user, '_isGroup', False):
            return ()

        # If we happen to know that the user's object type
        # doesn't match this auth plugin, avoid querying SF
        sf_obj_type = self._get_sf_obj_type_hints().get(user.getId())
        if sf_obj_type and sf_obj_type != self._sf_object_type:
            return ()
        
        view_name = createViewName('getPropertiesForUser', user.getId())
        keywords = {'plugin_id': self.getId()}
        cached_info = self.ZCacheable_get(view_name=view_name, keywords=keywords, default=_marker)
        if cached_info is not _marker:
            return cached_info

        if not self.listSalesforceFields():
            warnings.warn("""Configuration Error: You've configured your Salesforce Auth Plugin as an"""
                          """ IPropertiesPlugin, but provide no properties to manage.""",
                          UserWarning,
                          stacklevel=1)
            retval = MutablePropertySheet(self.id)
        else:
            soql = "SELECT %s FROM %s WHERE %s='%s'" % (
                ', '.join(self.listSalesforceFields()), self._sf_object_type,
                 self.getLoginFieldName(), user.getId())
            res = self._getSFConnection().query(soql)
            
            if res['size'] != 1:
                logger.debug("Found %s users for id: [%s]. Can't return user info."
                                % (res['size'], user.getId()))
                retval = None
            else:
                retval = self._buildPropertySheet(res[0])
                
        self.ZCacheable_set(retval, view_name=view_name, keywords=keywords)
        return retval
    
    def _buildPropertySheet(self, res):
        data = dict(sf_obj_type = self._sf_object_type)
        
        for localname, salesforcename in self.listLocalToSFMappings():
            data[localname]=res[salesforcename]
            if isinstance(data[localname], date):
                # coerce python date objects into Plone-friendly DateTime objects
                data[localname] = DateTime(data[localname].strftime("%Y/%m/%d"))
            elif data[localname] is None:
                # XXX quick fix for issue where the property sheet can't
                # guess the type of None values.  The correct way to solve this
                # would be to manually set up the property schema based on the
                # SF field types returned by describeSObjects
                data[localname] = ''
        
        # 4) instantiate the appropriate MPS()
        return MutablePropertySheet(self.id, **data)
    
    #
    # IMutablePropertiesPlugin implementation
    #
    security.declarePrivate('setPropertiesForUser')
    def setPropertiesForUser(self, user, propertysheet):
        logger.debug('calling setPropertiesForUser')
        props = dict(propertysheet.propertyItems())
        self.updateUserInfo(user, set_id=None, set_info=props)
    
    security.declarePrivate('deleteUser')
    def deleteUser(self, user_id):
        """Remove properties stored for a user."""
        pass
    
    #
    # IUpdatePlugin implementation
    #
    security.declarePrivate('updateUserInfo')
    def updateUserInfo(self, user, set_id, set_info):
        if set_id is not None:
            raise NotImplementedError, "Cannot currently rename the user id of a user"
        
        # Make sure we only have one user in salesforce with this id
        soql = "SELECT Id FROM %s WHERE %s='%s'" % (
            self._sf_object_type, self.getLoginFieldName(), user.getId()
            )
        res = self._getSFConnection().query(soql)

        # make sure our result numbers are correct
        if res['size'] != 1:
            logger.debug("Found %s users for id: [%s]. Can't set user properties" 
                            % (res['size'], user.getId()))
            return
        
        data = dict(type=self._sf_object_type, Id=res['records'][0]['Id'])
        # Iterate over fields our plugin maintains
        for localname, sfname in self.listLocalToSFMappings():
            # Map these values from the dictionary to their SF equivalents
            if set_info.has_key(localname):
                # Build dictionary of values to call update(), with a little type-checking
                if isinstance(set_info[localname], DateTime):
                    data[sfname] = DateTime2datetime(set_info[localname])
                elif set_info[localname] == 'on' and self._isBooleanField(sfname):
                    data[sfname] = True
                else:
                    data[sfname] = set_info[localname]
        
        logger.debug(data)
        res = self._getSFConnection().update(data)
        
        # invalidate the properties cache
        view_name = createViewName('getPropertiesForUser', user.getId())
        self.ZCacheable_invalidate(view_name=view_name)
    
    
    def _isBooleanField(self, sfFieldName):
        return self._dataTypeForSFField(self._sf_object_type, sfFieldName) == 'boolean'
        

InitializeClass(PropertyManagementMixin)
