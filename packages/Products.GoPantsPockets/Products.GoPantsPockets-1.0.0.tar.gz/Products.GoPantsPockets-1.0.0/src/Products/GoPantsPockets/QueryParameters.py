# -*- coding: utf-8 -*-
#
# File: QueryParameters.py
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

from Products.GoPantsPockets.config import *

##code-section module-header #fill in your manual code here
from zLOG import LOG, INFO, WARNING, DEBUG, TRACE, PROBLEM, ERROR
##/code-section module-header

schema = Schema((


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

QueryParameters_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class QueryParameters(OrderedBaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IQueryParameters)

    meta_type = 'QueryParameters'
    _at_rename_after_creation = True

    schema = QueryParameters_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getKeyValuePairObjects')
    def getKeyValuePairObjects(self):
        """
        """
        return [kvp for kvp in self.objectValues('KeyValuePair') if kvp.getActive()]

    security.declareProtected("Perform_GoQuery", 'getKeyValuePairs')
    def getKeyValuePairs(self):
        """
        """
        kvps = {}
        for kvp in self.getKeyValuePairObjects():
            if kvp.getActive():
                kvps[kvp.getKey()] = eval(kvp.getValue())
        return kvps

    security.declareProtected("Perform_GoQuery", 'aggregateKeywords')
    def aggregateKeywords(self,**kw):
        """
        """
        aggregated_kw = kw.copy()
        for k,v in self.getKeyValuePairs().items():
            if not hasattr(aggregated_kw, k):
                aggregated_kw[k] = v
        return aggregated_kw


registerType(QueryParameters, PROJECTNAME)
# end of class QueryParameters

##code-section module-footer #fill in your manual code here
##/code-section module-footer

