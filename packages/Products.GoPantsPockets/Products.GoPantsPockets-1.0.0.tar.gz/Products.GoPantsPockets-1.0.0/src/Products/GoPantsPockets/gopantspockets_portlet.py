# -*- coding: utf-8 -*-
#
# File: gopantspockets_portlet.py
#
# Copyright (c) 2012 by "Georg Gogo. BERNHARD" <"gogo@bluedynamics.com">
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """"Georg Gogo. BERNHARD" <"gogo@bluedynamics.com">"""
__docformat__ = 'plaintext'

##code-section module-header #fill in your manual code here
from zope import schema
##/code-section module-header


from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.CMFPlone import PloneMessageFactory as _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Igopantspockets_portlet(IPortletDataProvider):
    """A portlet which renders a StoredQuery.
    """
    querySelection = schema.List(
            title = _(u"Used Queries"),
            value_type = schema.Choice(
                source = "collective.FSB.GoPantsPockets.gopantspockets_portlet.QueryVocabularyFactory",
            ),
        )

class Assignment(base.Assignment):

    implements(Igopantspockets_portlet)

    title = _(u'GoPantsPockets Portlet')

    ##code-section assignment-body #fill in your manual code here
    def __init__(self, querySelection=[]):
        self.querySelection = []
    ##/code-section assignment-body



class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/gopantspockets_portlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        ##code-section __init__ method #fill in your manual code here
        ##/code-section __init__ method

    ##code-section class-header_Renderer #fill in your manual code here
    def getStoredQueries(self):
        return [query for query in self.context.portal_gopantspockets.getStoredQueries() if query.id in self.data.querySelection]
    ##/code-section class-header_Renderer




class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

    ##code-section addform-body #fill in your manual code here
    ##/code-section addform-body


##code-section module-footer #fill in your manual code here

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

class QueryVocabulary(object):
    implements(IVocabularyFactory)
    def __call__(self, context):
        queries = context.portal_gopantspockets.getStoredQueries()
        items = [SimpleTerm(query.id, query.id, query.title_or_id()) for query in queries if not query.getHidden()]
        return SimpleVocabulary(items)

QueryVocabularyFactory = QueryVocabulary()

from zope.formlib import form
class EditForm(base.EditForm):
    form_fields = form.Fields(Igopantspockets_portlet)
    label = _(u"Edit GoPantsPockets Portlet")
    description = _(u"This portlet displays the selected queries (and their interactive input fields)")
    
##/code-section module-footer
