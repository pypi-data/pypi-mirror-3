# -*- coding: utf-8 -*-
#
# File: KeyValuePair.py
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

    StringField(
        name='key',
        widget=StringField._properties['widget'](
            label='Key',
            label_msgid='GoPantsPockets_label_key',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    StringField(
        name='value',
        widget=StringField._properties['widget'](
            label='Value',
            label_msgid='GoPantsPockets_label_value',
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

KeyValuePair_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class KeyValuePair(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IKeyValuePair)

    meta_type = 'KeyValuePair'
    _at_rename_after_creation = True

    schema = KeyValuePair_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """
        infos = []
        if not self.getActive():
            infos.append("(inactive)")
        infos.append(self.title_or_id())
        infos.append("key: %s" % self.getKey())
        infos.append("value: %s" % self.getValue())
        s = " / ".join(infos)
        return s


registerType(KeyValuePair, PROJECTNAME)
# end of class KeyValuePair

##code-section module-footer #fill in your manual code here
##/code-section module-footer

