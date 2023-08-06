# -*- coding: utf-8 -*-
#
# File: SortRule.py
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
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.GoPantsPockets.config import *

##code-section module-header #fill in your manual code here
from zLOG import LOG, INFO, WARNING, DEBUG, TRACE, PROBLEM, ERROR
##/code-section module-header

schema = Schema((

    StringField(
        name='sortFieldName',
        widget=StringField._properties['widget'](
            description="Can be a tal style variable like gopantspockets_metadata/title_or_id",
            label='Sortfieldname',
            label_msgid='GoPantsPockets_label_sortFieldName',
            description_msgid='GoPantsPockets_help_sortFieldName',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    LinesField(
        name='sortSequence',
        widget=LinesField._properties['widget'](
            label='Sortsequence',
            label_msgid='GoPantsPockets_label_sortSequence',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    BooleanField(
        name='reversed',
        widget=BooleanField._properties['widget'](
            label='Reversed',
            label_msgid='GoPantsPockets_label_reversed',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    BooleanField(
        name='active',
        default=1,
        widget=BooleanField._properties['widget'](
            label='Active',
            label_msgid='GoPantsPockets_label_active',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

SortRule_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class SortRule(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.ISortRule)

    meta_type = 'SortRule'
    _at_rename_after_creation = True

    schema = SortRule_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('sort')
    def sort(self,items):
        """
        """
        if not self.getActive():
            return items

        sortfieldname = self.getSortFieldName()
        if not sortfieldname:
            return items

        sortsequence = self.getSortSequence()
        decorations = {}
        for i in xrange(len(sortsequence)):
            decorations[sortsequence[i]] = i

        class Missing:
            pass
        missing = Missing()

        decorated = []
        untouched = []
        for item in items:
            fieldvalue = self.getChainedAttribute(item, sortfieldname)

            if decorations:
                decoration = decorations.get(fieldvalue, missing)
            else:
                if type(fieldvalue) == type(""):
                    fieldvalue = fieldvalue.upper()
                decoration = fieldvalue
            if decoration != missing:
                decorated.append((decoration, item))
            else:
                untouched.append(item)

        decorated.sort()
        items = [i[1] for i in decorated]
        if self.getReversed():
            items.reverse()

        items = items + untouched

        return items

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """
        infos = []
        infos.append("sortFieldName: %s" %self.getSortFieldName())
        infos.append("sortSequence: %s" % repr(self.getSortSequence()))
        infos.append("reversed %s" % self.getReversed())
        s = " / ".join(infos)
        return s


registerType(SortRule, PROJECTNAME)
# end of class SortRule

##code-section module-footer #fill in your manual code here
##/code-section module-footer

