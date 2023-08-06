# -*- coding: utf-8 -*-
#
# File: RemoteQueryServer.py
#
# Copyright (c) 2012 by "Georg Gogo. BERNHARD" <"gogo@bluedynamics.com">
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """"Georg Gogo. BERNHARD" <"gogo@bluedynamics.com">"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope import interface
from zope.interface import implements
import interfaces
from Products.GoPantsPockets.IRemoteQueryServer import IRemoteQueryServer
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.GoPantsPockets.config import *

##code-section module-header #fill in your manual code here
from zLOG import LOG, INFO, WARNING, DEBUG, TRACE, PROBLEM, ERROR
##/code-section module-header

schema = Schema((

    TextField(
        name='description',
        widget=TextAreaWidget(
            label='Description',
            label_msgid='GoPantsPockets_label_description',
            i18n_domain='GoPantsPockets',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

RemoteQueryServer_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class RemoteQueryServer(OrderedBaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IRemoteQueryServer, IRemoteQueryServer)

    meta_type = 'RemoteQueryServer'
    _at_rename_after_creation = True

    schema = RemoteQueryServer_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('dispatchRemoteQuery')
    def dispatchRemoteQuery(self,kw):
        """
        """
        raise "dispatchRemoteQuery has not been implemented."

    security.declarePublic('applyRewriteRules')
    def applyRewriteRules(self, resultSet):
        """
        """
        rwrules = self.objectValues('RewriteRule')
        res = []

        for item in resultSet:
            for rwrule in rwrules:
                item = rwrule.rewrite(item)

            item['gopantspockets_metainfo'] = {\
                    'RemoteQueryServer':self.id,
                    'userID':self.getUserID(),
                    'columns':self.getColumnsOfInterest(),
                    }

            # @@@ Gogo. think about it ... ??? ....
            # @@@ UID, permalink and Title are mandatory fields, even for REST results;
            # @@@ You will have to provide them with RewriteRules or whatever...
            if item.get('UID'):
                item['gopantspockets_metainfo']['UID'] = item.get('UID')
            else:
                item['gopantspockets_metainfo']['UID'] = None

            if item.get('permalink'):
                item['gopantspockets_metainfo']['permalink'] = item.get('permalink')
            elif item.get('getURL'):
                item['gopantspockets_metainfo']['permalink'] = item.get('getURL')
            else:
                item['gopantspockets_metainfo']['permalink'] = None

            if item.get('Title') or item.get('id'):
                item['gopantspockets_metainfo']['title_or_id'] = item.get('Title') or item.get('id')
            else:
                item['gopantspockets_metainfo']['title_or_id'] = None
                
            res.append(item)
        return res

    security.declarePublic('deduplicateResultSet')
    def deduplicateResultSet(self, resultSet):
        """
        """
        dejavu = {}
        filtered = []
        for item in resultSet:
            uid = item['gopantspockets_metainfo']['UID']
            if not uid:
                filtered.append(item)
            elif not dejavu.get(uid):
                filtered.append(item)
                dejavu[uid] = True
        resultset = filtered
        return filtered

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """

        raise "GoPantsPockets:RemoteQueryServer.getInfo has not been implemented."


registerType(RemoteQueryServer, PROJECTNAME)
# end of class RemoteQueryServer

##code-section module-footer #fill in your manual code here
##/code-section module-footer

