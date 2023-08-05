from zope.interface import Interface

class IMappingUI(Interface):
    
    def setMappingFromUI(mappingList, mapType='properties'):
        """Converts a UI-friendly mapping of plone-to-salesforce fields
           into the internally stored format.
        """
    
    def getLocalToSFMapping(mapType='properties'):
        """Returns the current mapping in dictionary format 
           of the Plone-centric (i.e. what's in the propertysheet)
           to Salesforce-centric (i.e. the fields on the SFObject) fields.  
           Plone-centric names serve as the keys.
           
           There be multiple mappings stored as instance attributes.  Available
           options include: "properties" (default), "auth".  The preferred mapping for 
           retrieval can be passed as a parameter.
           
           For example:
           
                {
                    'assistant_name':'AssistantName',
                    'department':'Department',
                }
           
        """
    
    def setLocalToSFMapping(dictionary, mapType='properties'):
        """Sets the current mapping in dictionary format 
           of the Plone-centric (i.e. what's in the propertysheet)
           to Salesforce-centric (i.e. the fields on the SFObject) fields as passed
           in the dictionary parameter.  Plone-centric names serve as the keys.
           
           There be multiple mappings stored as instance attributes.  Available
           options include: "properties" (default), "auth".  The preferred mapping for 
           configuration can be passed as a parameter.
           
           For example:
           
           propMap = {
                    'assistant_name':'AssistantName',
                    'department':'Department',
                }
           
           setLocalToSFMapping(propMap, mapType='properties')
        """
    
    def listMappingForLinesField(mapType='properties'):
        """Returns mapping of plone to Salesforce fieldnames in a format
           appropriate to display in the UI:
           
               username|Username__c
               password|Password__c
               email|MyCustomField__c
        
        """
class IUserManagementPluginPropertyManager(Interface):
    """Mapping class providing convenience
       methods for determining how we interact
       with specific SObjects.
    """
    def getSFObjectTypes():
        """Returns a list of all content types defined in the configured
           Salesforce instance.
        """
    
    def getSFObjectType():
        """Returns the currently chosen SFObject type as
           a string for the given plugin.
        """
    
    def setSFObjectType(newType):
        """Sets the SFObject type as
           a string on the given plugin.
        """
    
    def getLoginFieldName():
        """Returns the name of the Salesforce field used to store the 
           login name for authentication.
        """
    
    def getPasswordFieldName():
        """Returns the name of the Salesforce field used to store the
           password for authentication.
        """
    
    def getAuthConditionClause():
        """Returns an additional SOQL statement for authentication 
           of site users to be appended to the usual username and password
           query.
           
           For Example: 
           
                "AccountActive__c=True AND Email like '%@example.com'"
        """
    
    def setAuthConditionClause(authConditionClause=''):
        """Sets an additional SOQL statement for authentication 
           of site users to be appended to the usual username and password
           query.
           
           For Example: 
           
                "AccountActive__c=True AND Email like '%@example.com'"
        """
    
    def setEncryptionAlgorithm(encryptionName='plain'):
        """Sets the encryption algorithm to apply when storing the user's
           password when implementing IUserAuthentication.
           See the configure.zcml file for all the supported algorithms.
        """
    
    def getEncryptionAlgorithm():
        """Returns the current choice of encryption algorithm for storing
           a user's password in Salesforce.
        """
    
    def listValidEncryptionAlgorithms():
        """Returns a list of names of all the available encryption algorithms
        """
    
    def manage_updateConf(authConditionClause='', localToSFFieldMapping=[], REQUEST=None):
        """Neccessary ZMI configuration
        """
    

