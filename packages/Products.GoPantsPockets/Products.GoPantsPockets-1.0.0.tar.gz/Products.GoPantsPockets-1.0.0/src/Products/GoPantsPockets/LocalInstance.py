# -*- coding: utf-8 -*-
#
# File: LocalInstance.py
#
# Copyright (c) 2012 by Georg Gogo. BERNHARD <gogo@bluedynamics.com>
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Georg Gogo. BERNHARD <gogo@bluedynamics.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.GoPantsPockets.RemoteQueryServer import RemoteQueryServer
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.GoPantsPockets.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, INFO, WARNING, DEBUG, TRACE, PROBLEM, ERROR
##/code-section module-header

schema = Schema((


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

LocalInstance_schema = BaseFolderSchema.copy() + \
    getattr(RemoteQueryServer, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class LocalInstance(BaseFolder, RemoteQueryServer, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.ILocalInstance)

    meta_type = 'LocalInstance'
    _at_rename_after_creation = True

    schema = LocalInstance_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('dispatchRemoteQuery')
    def dispatchRemoteQuery(self,userID,**kw):
        """
        """
        columns = self.getColumnsOfInterest()
        brains = self.portal_catalog.searchResults(**kw)
        LOG("GoPantsPockets:LocalInstance.dispatchRemotqQuery",DEBUG,"parameters: %s, %s " % (repr(userID), repr(kw),))
        print("GoPantsPockets:LocalInstance.dispatchRemotqQuery",DEBUG,"parameters: %s, %s " % (repr(userID), repr(kw),))
        resultSet = self.portal_gopantspockets.brainsToDict(brains, columns)
        resultSet = self.applyRewriteRules(resultSet)
        resultSet = self.deduplicateResultSet(resultSet)

        for item in resultSet:
            item['gopantspockets_metainfo']['permalink'] = self.getBaseURL()+"/resolveuid/"+item.get('UID')+"/view"

        return resultSet

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """
        infos = []
        infos.append("baseURL: %s" % self.getBaseURL())
        return " / ".join(infos)


    security.declarePublic('getBaseURL')
    def getBaseURL(self):
        """
        """
        base_url = getToolByName(self, 'portal_url').getPortalObject().absolute_url()
        return base_url


registerType(LocalInstance, PROJECTNAME)
# end of class LocalInstance

##code-section module-footer #fill in your manual code here
##/code-section module-footer

