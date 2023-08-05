import logging
import copy

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PluggableAuthService.utils import createViewName

logger = logging.getLogger("salesforceauthplugin")

class UserEnumerationMixin:
    """Implement Products.PluggableAuthService.interfaces.plugins.IUserEnumerationPlugin
    """
    security = ClassSecurityInfo()

    #
    #   IUserEnumerationPlugin
    #
    security.declarePrivate('enumerateUsers')
    def enumerateUsers(self, id=None, login=None, exact_match=False,
        sort_by=None, max_results=None, **kw):
        """ See IUserEnumeration
        """
        # # TODO: login vs. id USERNAME_FIELD vs. LOGIN_FIELD
        logger.debug('calling enumerateUsers()...')
        
        view_name = createViewName('enumerateUsers')

        if isinstance(id, unicode):
            id = [id.encode()]
        if isinstance(id, basestring):
            id = [id]
        if isinstance(login, basestring):
            login = [login]
        id_or_login = set([])
        if id:
            id_or_login = id_or_login.union(set(id))
        if login:
            id_or_login = id_or_login.union(set(login))

        # If we're looking for an exact match and we happen to know that
        # its object type doesn't match this auth plugin, avoid querying SF
        if exact_match and len(id_or_login) == 1:
            sf_obj_type = self._get_sf_obj_type_hints().get(list(id_or_login)[0])
            if sf_obj_type and sf_obj_type != self._sf_object_type:
                return ()
        
        # we don't support search by e-mail for now
        if 'email' in kw:
            return ()
        
        # Check cached data
        keywords = copy.deepcopy(kw)
        info = {
            'plugin_id': self.getId(),
            'id_or_login': tuple(id_or_login),
            'sort_by': sort_by,
            'exact_match': exact_match,
            'max_results': max_results,
        }
        keywords.update(info)
        cached_info = self.ZCacheable_get(view_name=view_name,
                                          keywords=keywords)
        if cached_info is not None:
            return cached_info
        
        if kw.has_key('fullname'):
            results = self._fullNameSearch(kw['fullname'], exact_match, max_results)
        else:
            results = self._idOrLoginSearch(id_or_login, exact_match, max_results)
        
        results = self._truncateAndSort(results, max_results, sort_by)
        retvals = tuple(results)
        
        # Cache data upon success
        self.ZCacheable_set(retvals, view_name=view_name, keywords=keywords)
    
        return retvals

    #
    # IUserEnumerationPlugin helper methods
    # 
    security.declarePrivate('_extractQueryDataForEnum')
    def _extractQueryDataForEnum(self, res):
        """Accepts a Salesforce.com query result
           set and extracts id, login, and sets pluginid
           for the IUserEnumerationPlugin
        """
        results = list()
        for r in res['records']:
            username = r[self.getLoginFieldName()]
            
            # populate properties cache
            view_name = createViewName('getPropertiesForUser', username)
            property_sheet = self._buildPropertySheet(r)
            self.ZCacheable_set(property_sheet, view_name=view_name, keywords={'plugin_id': self.getId()})
            
            # populate enumerateUsers (as used for _verifyUser) cache
            key = {'plugin_id': self.getId(), 'id_or_login': (username,), 'sort_by': None, 'exact_match': True, 'max_results': None}
            value = ({'id': username, 'login': username, 'pluginid': self.getId()} ,)
            view_name = createViewName('enumerateUsers')
            self.ZCacheable_set(value, view_name=view_name, keywords=key)
            
            self._get_sf_obj_type_hints()[username] = self._sf_object_type
            
            data = dict(id=username, login=username, 
                pluginid=self.getId())
            results.append(data)
        return results
    
    security.declarePrivate('_buildAuthenticationQuery')
    def _buildEnumerationQuery(self, query):
        """Append the additional 'where' clause to our soql statement"""
        addlConditionString = self.getAuthConditionClause()
        if query and addlConditionString:
            query += ' and ' + addlConditionString
        elif addlConditionString:
            query = addlConditionString
        return query
    
    security.declarePrivate('_fullNameSearch')
    def _fullNameSearch(self, fullname, exact_match, max_results):
        # Get the union of both of the field mappings, so we can look for 'fullname' as a
        # key in both of them
        mapping = dict()
        mapping.update(self.getLocalToSFMapping('properties'))
        mapping.update(self.getLocalToSFMapping('auth'))
        if not mapping.has_key('fullname'):
            # punt to login or id search
            return self._idOrLoginSearch([fullname], exact_match, max_results)
        else:
            # search specific
            if exact_match:
                query = "%s='%s'" % (mapping['fullname'], fullname)
            else:
                query = "%s like '%%%s%%'" % (mapping['fullname'], fullname)  
                return self._doRunQuery(query, max_results)                   
    
    security.declarePrivate('_doRunQuery')
    def _doRunQuery(self, query, max_results):
        results = list()
        fields = set()
        fields.add(self.getLoginFieldName())
        for fieldname in self.listSalesforceFields():
            fields.add(fieldname)
        fields = ', '.join(fields)
        soql = "SELECT %s FROM %s" % (fields, self._sf_object_type)
        whereClause = self._buildEnumerationQuery(query)
        if whereClause:
            soql += ' WHERE ' + whereClause
        res = self._getSFConnection().query(soql)
        results.extend(self._extractQueryDataForEnum(res))

        # if our query could return more data and we're not
        # up against the limits of our max_results, we
        # need to call queryMore
        while not res['done']:
            if max_results and len(results) >= max_results:
                break
            res = self._getSFConnection().queryMore(res['queryLocator'])
            results.extend(self._extractQueryDataForEnum(res))
        
        return results
    
    security.declarePrivate('_idOrLoginSearch')
    def _idOrLoginSearch(self, id_or_login, exact_match, max_results):
        results = list()
        
        if len(id_or_login) == 0:
            id_or_login = (None,)
                         
        for user_id in id_or_login:
            if user_id is None:
                # search all
                query = ""
            else:
                # search specific
                if exact_match:
                    query = "%s='%s'" % (self.getLoginFieldName(), user_id)
                else:
                    query = "%s like '%%%s%%'" % (self.getLoginFieldName(), user_id)
            
            results.extend(self._doRunQuery(query, max_results))
        return results
    
    security.declarePrivate('_truncateAndSort')
    def _truncateAndSort(self, results, max_results, sort_by):
        if max_results:
            results = results[:max_results]
        if sort_by:
            results.sort(key=lambda a: a[sort_by])
            
        return results

InitializeClass(UserEnumerationMixin)