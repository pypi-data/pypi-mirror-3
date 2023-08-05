import logging

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Cache import Cacheable
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName

# PAS
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

logger = logging.getLogger("salesforceauthplugin")

class SalesforceBasePluginMixin(BasePlugin, Cacheable):
    """Our base plugin for mixin with interface specific
       plugins
    """
    security = ClassSecurityInfo()
    meta_type = 'Salesforce Auth Plugin'

    #
    # Internal API
    #
    security.declarePrivate("_getSFConnection")
    def _getSFConnection(self):
        # old code used to set a (persisted! oops!) baseconnector
        # attribute ... make sure we clean that up
        if 'baseconnector' in self.__dict__:
            del self.baseconnector

        pas=self._getPAS()
        site=aq_parent(pas)
        return getToolByName(site, 'portal_salesforcebaseconnector')

InitializeClass(SalesforceBasePluginMixin)
