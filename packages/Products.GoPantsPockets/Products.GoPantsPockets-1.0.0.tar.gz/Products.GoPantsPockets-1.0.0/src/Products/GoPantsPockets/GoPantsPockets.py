# -*- coding: utf-8 -*-
#
# File: GoPantsPockets.py
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


from Products.CMFCore.utils import UniqueObject

    
##code-section module-header #fill in your manual code here
from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import AccessInactivePortalContent
from zLOG import LOG, INFO, WARNING, DEBUG, TRACE, PROBLEM, ERROR
import cPickle
from time import time
from plone.memoize.ram import cache
from plone.memoize.ram import global_cache
global_cache.invalidateAll()


def gopantspockets_cacheDescriptor(*args, **kwargs):
   # import pdb;pdb.set_trace()
    _self = args[1]
    gopantspockets_queryIDs = args[2]
    if not _self.getCacheTime():
        cachebag = str(time())
        LOG("GoPantsPockets:GoPantsPockets.gopantspockets_cacheDescriptor", INFO, "Cache was not used, because CacheTime is not set. (To enable caching go to portal_gopantspockets and define a CacheTime)")
    else:
        t = time() // (_self.getCacheTime())
        cachebag = "%s %s %s %s" % (t, _self.getUserID(), repr(gopantspockets_queryIDs), repr(kwargs))
    print "CACHEBAG:", cachebag
    return cachebag


##/code-section module-header

schema = Schema((

    IntegerField(
        name='cacheTime',
        default=300,
        widget=IntegerField._properties['widget'](
            description="Time to cache search results (in seconds)",
            label='Cachetime',
            label_msgid='GoPantsPockets_label_cacheTime',
            description_msgid='GoPantsPockets_help_cacheTime',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    LinesField(
        name='filteredKWs',
        default='b_start\nb_end\nb_size\nsubmit\n-C',
        widget=LinesField._properties['widget'](
            description="Keys to filter from search queries, e.g. Plone variables for batch processing. Filter everything that might affect caching in a negative way.",
            label='Filteredkws',
            label_msgid='GoPantsPockets_label_filteredKWs',
            description_msgid='GoPantsPockets_help_filteredKWs',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

GoPantsPockets_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class GoPantsPockets(UniqueObject, OrderedBaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IGoPantsPockets)

    meta_type = 'GoPantsPockets'
    _at_rename_after_creation = True

    schema = GoPantsPockets_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        OrderedBaseFolder.__init__(self,'portal_gopantspockets')
        self.setTitle('')

        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer


    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()

        ##code-section post-edit-method-footer #fill in your manual code here
        ##/code-section post-edit-method-footer


    # Methods

    security.declarePublic('action_dispatchStoredQuerys')
    def action_dispatchStoredQuerys(self, REQUEST):
        """ This action is being called from forms, filtered keywords are
        being discarded, "SearchableText" is being extended with asterix,
        gopantspockets_queryIDs are being looked up and then all queries are dispatched.
        """

        from time import time
        start = time()

        form = REQUEST.form

        kw = {}
        kw = [k for k in form.items() if k[0] not in self.getFilteredKWs()]
        kw = dict(kw)

        gopantspockets_queryIDs = form.get('gopantspockets_queryIDs')
        if gopantspockets_queryIDs:
            if type(gopantspockets_queryIDs) != type([]):
                gopantspockets_queryIDs = [gopantspockets_queryIDs]
            del kw['gopantspockets_queryIDs']

        if form.get('SearchableText'):
            search_text = ""
            for term in form.get('SearchableText','').split():
                if term.rfind("*") == -1 :
                    search_text = search_text + term + "* "
                else:
                    search_text = search_text + term + " "
            kw['SearchableText'] = search_text

        results = self.dispatchStoredQuerys(gopantspockets_queryIDs, **kw)

        end = time()
        print "Query took %s seconds." % (end-start)

        for sort_rule in self.getSortRules():
            results = sort_rule.sort(results)

        return results

    security.declareProtected("Perform_GoQuery", 'dispatchStoredQuerys')
    @cache(gopantspockets_cacheDescriptor)
    def dispatchStoredQuerys(self, queryIDs, **kw):
        """<p>Performs given StoredQueries or all if no IDs are
        provided.</p>
        """
        # print "dispatchStoredQuerys has been called to really perform a search..."
        kw = kw.copy()
        if queryIDs:
            queries = [query for query in self.objectValues('StoredQuery') if query.id in queryIDs]
        else:
            queries = self.objectValues('StoredQuery')
        # print "Queries: %s" % repr(queries)
        res = []
        for query in queries:
            res += query.doQuery(**kw)
        return res

    security.declareProtected("Perform_GoQuery", 'dispatchSearchResults')
    def dispatchSearchResults(self,serverIDs,**kw):
        """<p>Ccollects search results from all XMLRPCServers, using the
        keywords given. No saved query is performed.</p>
        """
        if serverIDs:
            servers = [server for server in self.getXMLRPCServers() if server.id in serverIDs]
        else:
            servers = self.getXMLRPCServers()
        res = []
        for server in servers:
            res += server.dispatchRemoteQuery(self.getUserID(), **kw)
        return res

    security.declareProtected("Perform_GoQuery", 'handleRemoteQuery')
    def handleRemoteQuery(self, pickled_query):
        """<p>Collects search results from all QueryServers using the
        keywords given.</p>
        """

        args = cPickle.loads(pickled_query)
        userID = args['userID']
        kw = args['kw']
        columns = args['columns']

        LOG("GoPantsPockets:GoPantsPockets.handleRemoteQuery", DEBUG, "handleRemoteQuery(userID: %s; kw: %s; columns: %s)" % (repr(userID), repr(kw), repr(columns)))

        kw = kw.copy()
        show_inactive = kw.get("show_inactive", False)
        kw["allowedRolesAndUsers"] = self.getAllowedRolesAndUsers(userID)
        if not show_inactive and not _checkPermission(AccessInactivePortalContent, self):
            kw["effectiveRange"] = DateTime()
        brains = self.portal_catalog._catalog.searchResults(None, **kw)
        res = self.brainsToDict(brains, columns)

        payload = cPickle.dumps(res)
        return payload

    security.declareProtected("Perform_GoQuery", 'getUserID')
    def getUserID(self):
        """
        """
        membership_tool = getToolByName(self,'portal_membership')
        member = membership_tool.getAuthenticatedMember()
        if str(member) != 'Anonymous User':
            user = member.getUser()
            userId = user.getId()
        else:
            userId = ''
        return userId

    security.declarePublic('getStoredQueries')
    def getStoredQueries(self):
        """
        """
        return self.objectValues('StoredQuery')

    security.declarePublic('getRemoteQueryServers')
    def getRemoteQueryServers(self):
        """
        """
        return self.objectValues(['XMLRPCServer','RESTServer', 'LocalInstance',])

    security.declarePublic('invalidateCache')
    def invalidateCache(self):
        """
        """
        global_cache.invalidateAll()
        LOG("GoPantsPockets:GoPantsPockets.invalidateCache", INFO, "Cache has been invalidated")
        print "CACHE INVALIDATED!"

        LOG("GoPantsPockets:GoPantsPockets.invalidateCache", WARNING, "Cache has been not invalidated, this method is not implemented. Set cacheTime to a low value instead.")
        res = """
        <html><head></head><body>
        Cache has been not been invalidated - please set Cachetime to a low value instead. <a href="%s">Click here.</a>
        </body></html>
        """ \
        % (str(self.portal_gopantspockets.absolute_url())+"/edit",)
        return res

    security.declarePublic('repairQueryParameterObjects')
    def repairQueryParameterObjects(self):
        """
        """
        repaired = []
        from Products.Relations.processor import process

        queries = [b.getObject() for b in self.portal_catalog.searchResults(portal_type='StoredQuery', Language='all')]
        for query in queries:
            ris = query.getReferenceImpl('QueryParameters')
            triplets = [(ri.sourceUID, ri.targetUID, 'QueryParameters',) for ri in ris if ri.getContentObject() == None]
            if triplets:
                process(query, triplets)
                repaired.append(query)

        s = ""
        s += "Repaired Content Objects for %s relations:<br />\n" % len(repaired)
        for item in repaired:
            s += " %s<br />\n" % repr(item.absolute_url())
        return s

    security.declarePublic('brainsToDict')
    def brainsToDict(self, brains, columns):
        """
        """
        # Serialize it, don't critisize it!
        res = []
        for brain in brains:
            item = {}
            for column in columns:
                value = getattr(brain, column, None)
                typename = type(value).__name__
                if hasattr(value, '__call__'):
                    value = value()
                if typename == 'Missing':
                    value = None
                elif typename == 'Message':
                     value = unicode(value)
                     typename = type(value).__name__
                item[column] = value
            res.append(item)
        return res

    security.declarePublic('getChainedAttribute')
    def getChainedAttribute(self, item, attribute_chain, default=None):
        attributes = attribute_chain.split('/')
        value = item

        class Missing:
            pass
        missing = Missing()

        for attribute in attributes:
            if value == missing:
                value = default
                break
            value = value.get(attribute, missing)

        LOG("GoPantsPockets:GoPantsPockets.getChainedAttribute", DEBUG, "getChainedAttribute(item=%s, attribute_chain=%s, default=%s) returns %s" % (repr(item), repr(attribute_chain), repr(default), repr(value)))

        return value

    security.declarePublic('setChainedAttribute')
    def setChainedAttribute(self,item,attribute_chain,value=None):
        """
        """
        attributes = attribute_chain.split('/')

        class Missing:
            pass
        missing = Missing()

        field = item
        for attribute in attributes[:-1]:
            if field == missing:
                break
            field = field.get(attribute, missing)

        oldvalue = self.getChainedAttribute(item, attribute_chain)
        field[attributes[-1]] = value
        LOG("GoPantsPockets:GoPantsPockets.setChainedAttribute", DEBUG, "getChainedAttribute(item=%s, attribute_chain=%s, value=%s)" % (repr(item), repr(attribute_chain), repr(value)))

        return oldvalue

    security.declarePublic('getAllowedRolesAndUsers')
    def getAllowedRolesAndUsers(self,userID):
        """
        """
        allowedRolesAndUsers = []
        tool = getToolByName(self,'portal_membership')
        if userID:
            member = tool.getMemberById(userID)
            if member:
                user = member.getUser()
                allowedRolesAndUsers.append("user:%s" % user.getId())
                allowedRolesAndUsers = allowedRolesAndUsers + list(user.getRoles())
                if hasattr(aq_base(user), "getGroups"):
                    allowedRolesAndUsers = allowedRolesAndUsers + ["user:%s" % x for x in user.getGroups()]
        allowedRolesAndUsers.append("Anonymous")
        return allowedRolesAndUsers

    security.declarePublic('getColumnsOfInterest')
    def getColumnsOfInterest(self):
        """
        """
        columns = self.portal_catalog._catalog.names
        for additional in ('UID', 'getURL',):
            if additional not in columns:
                columns = columns + (additional,)
        return columns

    # Manually created methods

    security.declareProtected("Perform_GoQuery", 'getXMLRPCServers')
    def getXMLRPCServers(self):
        """
        """
        return self.objectValues('XMLRPCServer')

    security.declarePublic('getSortRules')
    def getSortRules(self):
        """
        """
        return [o for o in self.objectValues('SortRule') if o.getActive()]



registerType(GoPantsPockets, PROJECTNAME)
# end of class GoPantsPockets

##code-section module-footer #fill in your manual code here
##/code-section module-footer

