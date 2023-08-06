# -*- coding: utf-8 -*-
#
# File: InteractiveInput.py
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
        name='fieldName',
        widget=StringField._properties['widget'](
            label='Fieldname',
            label_msgid='GoPantsPockets_label_fieldName',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    StringField(
        name='label',
        widget=StringField._properties['widget'](
            label='Label',
            label_msgid='GoPantsPockets_label_label',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    TextField(
        name='description',
        widget=TextAreaWidget(
            label='Description',
            label_msgid='GoPantsPockets_label_description',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    StringField(
        name='inputType',
        widget=SelectionWidget(
            label='Inputtype',
            label_msgid='GoPantsPockets_label_inputType',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
        vocabulary=['Text', 'Number', 'Date'],
    ),
    StringField(
        name='defaultValue',
        widget=StringField._properties['widget'](
            label='Defaultvalue',
            label_msgid='GoPantsPockets_label_defaultValue',
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

InteractiveInput_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class InteractiveInput(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IInteractiveInput)

    meta_type = 'InteractiveInput'
    _at_rename_after_creation = True

    schema = InteractiveInput_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('validateInput')
    def validateInput(self):
        """
        """
        pass

    security.declarePublic('getInputValue')
    def getInputValue(self):
        """
        """
        pass

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """
        infos = []
        if not self.getActive():
            infos.append("(inactive)")
        infos.append(self.title_or_id())
        infos.append("fieldName: %s" % self.getFieldName())
        infos.append("inputType: %s" % self.getInputType())
        infos.append("defaultValue: %s" % self.getDefaultValue())
        s = " / ".join(infos)
        return s

    # security.declarePublic('renderInput')
    # def renderInput(self):
    #     """
    #     """
    #     input_type = self.getInputType()
    # 
    #     s = ""
    #     if input_type == "Text":
    #         s += "%s<input type='text' name='%s' value='%s' self.getExtraTags() />%s" % (self.getLabel(), self.getFieldName(), self.getDefaultValue(), self.getDescription())
    #     else:
    #         raise "Type %s Not implemented" % input_type
    # 
    #     return s

registerType(InteractiveInput, PROJECTNAME)
# end of class InteractiveInput

##code-section module-footer #fill in your manual code here
##/code-section module-footer

