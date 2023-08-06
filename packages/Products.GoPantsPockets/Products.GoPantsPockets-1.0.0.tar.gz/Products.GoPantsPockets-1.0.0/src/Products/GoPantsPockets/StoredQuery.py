# -*- coding: utf-8 -*-
#
# File: StoredQuery.py
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

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.Archetypes.ReferenceEngine import ContentReferenceCreator
from Products.Relations.field import RelationField
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
        write_permission="Manage portal",
    ),
    BooleanField(
        name='hidden',
        widget=BooleanField._properties['widget'](
            label='Hidden',
            label_msgid='GoPantsPockets_label_hidden',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    RelationField(
        name='iremotequeryservers',
        widget=RelationField._properties['widget'](
            label='Iremotequeryservers',
            label_msgid='GoPantsPockets_label_iremotequeryservers',
            i18n_domain='GoPantsPockets',
        ),
        multiValued=1,
        relationship='QueryParameters',
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

StoredQuery_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class StoredQuery(OrderedBaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IStoredQuery)

    meta_type = 'StoredQuery'
    _at_rename_after_creation = True

    schema = StoredQuery_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected("Perform_GoQuery", 'doQuery')
    def doQuery(self,**kw):
        """
        """
        res = []

        for server in self.getIremotequeryservers():
            query_parameters = self.getQueryParametersForServer(server)
            kw = query_parameters.aggregateKeywords(**kw)
            answers = server.dispatchRemoteQuery(self.getUserID(), **kw)
            for answer in answers:
                answer['gopantspockets_metainfo']['StoredQuery'] = self.id
            res += answers
        res = self.applyRewriteRules(res)
        res = self.sort(res)
        return res

    security.declareProtected("Perform_GoQuery", 'getQueryParametersForServer')
    def getQueryParametersForServer(self, server):
        """
        """
        serverUID = server.UID()
        query_parameters_for_server = [ref.getContentObject() for ref in self.getReferenceImpl() if ref.targetUID == serverUID]
        if len(query_parameters_for_server) != 1:
            raise "Too many QueryParameter objects for Server %s in %s" % (server.absolute_url(), self.absolute_url())
        return query_parameters_for_server[0]

    security.declarePublic('getSortRules')
    def getSortRules(self):
        """
        """
        return [o for o in self.objectValues('SortRule') if o.getActive()]

    security.declarePublic('applyRewriteRules')
    def applyRewriteRules(self,resultSet):
        """
        """
        rwrules = self.objectValues('RewriteRule')
        res = []
        for item in resultSet:
            for rwrule in rwrules:
                item = rwrule.rewrite(item)
        return resultSet

    security.declarePublic('getInteractiveInputs')
    def getInteractiveInputs(self):
        """
        """
        return self.objectValues('InteractiveInput')

    # Manually created methods

    def sort(self, items):
        sort_rules = self.getSortRules()
        for sort_rule in sort_rules:
            items = sort_rule.sort(items)
        return items



registerType(StoredQuery, PROJECTNAME)
# end of class StoredQuery

##code-section module-footer #fill in your manual code here
##/code-section module-footer

