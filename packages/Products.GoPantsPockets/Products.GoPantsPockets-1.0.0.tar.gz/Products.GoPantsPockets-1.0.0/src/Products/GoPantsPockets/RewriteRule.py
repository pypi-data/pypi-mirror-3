# -*- coding: utf-8 -*-
#
# File: RewriteRule.py
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
import re
##/code-section module-header

schema = Schema((

    StringField(
        name='rewriteFieldName',
        widget=StringField._properties['widget'](
            description="Can be a tal style variable like element1/element2",
            label='Rewritefieldname',
            label_msgid='GoPantsPockets_label_rewriteFieldName',
            description_msgid='GoPantsPockets_help_rewriteFieldName',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    StringField(
        name='find',
        widget=StringField._properties['widget'](
            description="e.g. (.*)",
            label='Find',
            label_msgid='GoPantsPockets_label_find',
            description_msgid='GoPantsPockets_help_find',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    StringField(
        name='replace',
        widget=StringField._properties['widget'](
            description="e.g. http://127.0.0.1:8080/Plone/\\1",
            label='Replace',
            label_msgid='GoPantsPockets_label_replace',
            description_msgid='GoPantsPockets_help_replace',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    BooleanField(
        name='regex',
        widget=BooleanField._properties['widget'](
            label='Regex',
            label_msgid='GoPantsPockets_label_regex',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    StringField(
        name='rewriteToFieldName',
        widget=StringField._properties['widget'](
            description="Deletes the original field and puts the rewritten data in a field with the name given here.",
            label='Rewritetofieldname',
            label_msgid='GoPantsPockets_label_rewriteToFieldName',
            description_msgid='GoPantsPockets_help_rewriteToFieldName',
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

RewriteRule_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class RewriteRule(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IRewriteRule)

    meta_type = 'RewriteRule'
    _at_rename_after_creation = True

    schema = RewriteRule_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected("Perform_GoQuery", 'rewrite')
    def rewrite(self,item):
        """
        """
        LOG("GoPantsPockets:RewriteRule.rewrite", DEBUG, "applying %s" % self.title_or_id())

        if not self.getActive():
            LOG("GoPantsPockets:RewriteRule", DEBUG, "Ignoring RewriteRule %s, it is not active" % repr(self.title_or_id()))
            return item

        fieldname = self.getRewriteFieldName()
        find = self.getFind()
        replace = self.getReplace()
        regex = self.getRegex()
        rewriteToFieldName = self.getRewriteToFieldName()

        class Missing:
            pass
        missing = Missing()

        before = self.getChainedAttribute(item, fieldname, missing)
        after = before

        if (before != missing) and find and replace:
            if not regex:
                after = before.replace(find, replace)
            else:
                if self.get('_regex') != find:
                    self._regex = find
                    self._re = re.compile(find)
                after = self._re.sub(replace, before)

        if not rewriteToFieldName:
            self.setChainedAttribute(item, fieldname, after)
        else:
#            self.delChainedAttribute(item, fieldname)
            self.setChainedAttribute(item, rewriteToFieldName, after)

        LOG("GoPantsPockets:RewriteRule", DEBUG, "Rewriting %s to %s [%s/%s]" % (repr(before), repr(after), repr(fieldname), repr(rewriteToFieldName)))
        # print "GoPantsPockets:RewriteRule", "Rewriting %s to %s [%s/%s]" % (repr(before), repr(after), repr(fieldname), repr(rewriteToFieldName))

        return item

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """
        infos = []
        infos.append("rewriteFieldName: %s" % self.getRewriteFieldName())
        infos.append("find: %s" % self.getFind())
        infos.append("replace: %s" % self.getReplace())
        infos.append("regex: %s" % self.getRegex())
        infos.append("rewriteToField: %s" % self.getRewriteToFieldName())
        infos.append("active: %s" % self.getActive())
        s = " / ".join(infos)
        return s


registerType(RewriteRule, PROJECTNAME)
# end of class RewriteRule

##code-section module-footer #fill in your manual code here
##/code-section module-footer

