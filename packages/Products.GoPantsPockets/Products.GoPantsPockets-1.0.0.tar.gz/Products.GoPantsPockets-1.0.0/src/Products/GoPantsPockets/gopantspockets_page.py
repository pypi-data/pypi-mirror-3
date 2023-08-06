# -*- coding: utf-8 -*-
#
# File: gopantspockets_page.py
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

    LinesField(
        name='querySelection',
        widget=MultiSelectionWidget(
            label='Queryselection',
            label_msgid='GoPantsPockets_label_querySelection',
            i18n_domain='GoPantsPockets',
        ),
        multiValued=1,
        vocabulary="getSelectableQueries",
    ),
    TextField(
        name='preText',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label='Pretext',
            label_msgid='GoPantsPockets_label_preText',
            i18n_domain='GoPantsPockets',
        ),
        default_output_type='text/html',
    ),
    TextField(
        name='postText',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label='Posttext',
            label_msgid='GoPantsPockets_label_postText',
            i18n_domain='GoPantsPockets',
        ),
        default_output_type='text/html',
    ),
    TextField(
        name='pythonHeadline',
        widget=TextAreaWidget(
            description="""You can use python to render a headline e.g. "We got %s hits!" % len(results)""",
            label='Pythonheadline',
            label_msgid='GoPantsPockets_label_pythonHeadline',
            description_msgid='GoPantsPockets_help_pythonHeadline',
            i18n_domain='GoPantsPockets',
        ),
    ),
    TextField(
        name='pythonItem',
        default=""""<a href='%s'>%s</a>" % (result['getURL'], result['gopantspockets_metainfo']['title_or_id'],)""",
        widget=TextAreaWidget(
            description="""You can use Python expressions here e.g. "Item from %s: %s %s" % (result['gopantspockets_metainfo']['StoredQuery'], result['getURL'], result['gopantspockets_metainfo']['title_or_id'],)""",
            label='Pythonitem',
            label_msgid='GoPantsPockets_label_pythonItem',
            description_msgid='GoPantsPockets_help_pythonItem',
            i18n_domain='GoPantsPockets',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

gopantspockets_page_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class gopantspockets_page(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.Igopantspockets_page)

    meta_type = 'gopantspockets_page'
    _at_rename_after_creation = True

    schema = gopantspockets_page_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getCurrentQueries')
    def getCurrentQueries(self):
        """
        """
        return [query for query in self.portal_gopantspockets.getStoredQueries() if query.id in self.getQuerySelection()]

    security.declarePublic('getSelectableQueries')
    def getSelectableQueries(self):
        """
        """
        return [query.id for query in self.portal_gopantspockets.getStoredQueries()]

    security.declarePublic('renderPython')
    def renderPython(self, expression, **kw):
        """
        """
        env = globals().copy()
        for k,v in kw.items():
            env[k]=v
        try:
            res = eval(str(expression), env)
        except Exception, e:
            LOG("GoPantsPockets:StoredQuery_Page.renderPython", ERROR, "%s occurred in eval(%s) with globals\n%s\n" % (str(e), expression, env))
            return str(e)
        return res


registerType(gopantspockets_page, PROJECTNAME)
# end of class gopantspockets_page

##code-section module-footer #fill in your manual code here
##/code-section module-footer

