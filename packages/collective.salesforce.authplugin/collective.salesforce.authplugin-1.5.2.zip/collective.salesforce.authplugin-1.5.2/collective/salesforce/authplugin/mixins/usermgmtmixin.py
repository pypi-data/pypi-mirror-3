import logging

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PluggableAuthService.utils import createViewName

from Products.PlonePAS.interfaces.plugins import IUserManagement
from Products.PlonePAS.interfaces.capabilities import IPasswordSetCapability, IDeleteCapability

from collective.salesforce.authplugin import encrypt

logger = logging.getLogger("salesforceauthplugin")

class UserManagementMixin:
    """Implement Products.PlonePAS.interfaces.plugins.IUserManagement,
       Products.PlonePAS.interfaces.capabilities.IPasswordSetCapability and
       Products.PlonePAS.interfaces.capabilities.IDeleteCapability.
    """
    
    default_encryption = encrypt.DEFAULT_ENCRYPTION
    
    security = ClassSecurityInfo()
    
    #
    #  IUserManagement
    #
    security.declarePrivate('doChangeUser')
    def doChangeUser(self, login, password, **kw):
        """Change a user's password. Only implements password changing
           which is required by IUserManagement.
        """
        encrypter = encrypt.find_encrypter(self.default_encryption)
        if encrypter is None:
            raise LookupError('Could not find an encrypter for "%s"'
                              % self.default_encryption)
        password = encrypter.encrypt(password)
        
        soql = "SELECT Id FROM %s WHERE %s='%s'" % (
            self._sf_object_type,
            self.getLoginFieldName(),
            login
            )
        res = self._getSFConnection().query(soql)
        if res['size'] != 1:
            logger.debug("Found %s users for id: [%s]. Can't return user info..." % (res['size'],login))
            return
        data = {"type": self._sf_object_type, 
                "Id": res['records'][0]['Id'],
                self.getPasswordFieldName(): password, }
        res = self._getSFConnection().update(data)
        
        # invalidate the authentication cache
        if self.ZCacheable_isCachingEnabled():
            view_name = createViewName('authenticateCredentials', login)
            self.ZCacheable_invalidate(view_name=view_name)
        
        # handle success is false with logger message
        if not res[0]['success']:
            logger.debug("A password updated for user %s produced "
                         "the following error message %s" % (login, res[0]['errors'][0]['message']))
            return
    
    security.declarePrivate('doDeleteUser')
    def doDeleteUser(self , login):
        """doDeleteUser require
        """
        return False
    
    #
    # IDeleteCapability
    #
    security.declarePrivate('allowDeletePrincipal')
    def allowDeletePrincipal(self, id):
        """See IDeleteCapability"""
        return False
        
    #
    # IPasswordSetCapability
    #
    security.declarePrivate('allowPasswordSet')
    def allowPasswordSet(self, id):
        """Check if we can set a users password."""
        
        # use the enumerateUsers cache if it exists, to prevent unneeded extra queries to Salesforce
        view_name = createViewName('enumerateUsers')
        keywords = {
            'id': None,
            'login': None,
            'exact_match': False,
            'sort_by': None,
            'max_results': None,
        }
        user_info = self.ZCacheable_get(view_name=view_name, keywords=keywords)
        if user_info is not None:
            return id in [u['id'] for u in user_info]
        
        # fall back to a SF query for just this user
        return self._getUserInfo(id)

InitializeClass(UserManagementMixin)

