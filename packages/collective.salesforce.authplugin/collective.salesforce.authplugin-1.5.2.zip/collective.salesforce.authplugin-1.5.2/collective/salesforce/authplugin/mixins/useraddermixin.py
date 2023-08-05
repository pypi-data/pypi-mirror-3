import logging
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PluggableAuthService.utils import createViewName
from collective.salesforce.authplugin import encrypt

logger = logging.getLogger("salesforceauthplugin")

class UserAdderMixin:
    """Implement Products.PluggableAuthService.interfaces.plugins.IUserAdderPlugin
    """
    security = ClassSecurityInfo()
    
    default_encryption = encrypt.DEFAULT_ENCRYPTION
    
    #
    #  IUserAdderPlugin
    #
    security.declarePrivate('doAddUser')
    def doAddUser(self, login, password):
        logger.debug('calling doAddUser()...')
        
        encrypter = encrypt.find_encrypter(self.default_encryption)
        if encrypter is None:
            raise LookupError('Could not find an encrypter for "%s"'
                              % self.default_encryption)
        password = encrypter.encrypt(password)
        
        soql = "SELECT Id FROM %s WHERE %s='%s'" % (self._sf_object_type,
            self.getLoginFieldName(), login)
        res = self._getSFConnection().query(soql)
        if res['size'] != 0:
            logger.debug("This username already exists in Salesforce.")
            return False
        data = dict()
        data['type'] = self._sf_object_type
        
        # describeSObject, so we can get a list of fields and determine requiredness
        required_fields = self._getSFConnection().listFieldsRequiredForCreation(self._sf_object_type)
        
        # iterate fields to get a list of *really* required fields
        for required_field in required_fields:
            # put login in all fields by default 
            # (note: this will be overidden by mapped properties if configured)
            data[required_field] = login
        
        data[self.getLoginFieldName()] = login
        data[self.getPasswordFieldName()] = password
        res = self._getSFConnection().create(data)
        if res[0]['success']:
            # invalidate the user enumeration cache
            view_name = createViewName('enumerateUsers')
            self.ZCacheable_invalidate(view_name=view_name)
            
            return True
        return False # if we have some salesforce create error, present this in a logical non-swallowable way
    
InitializeClass(UserAdderMixin)