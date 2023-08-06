# -*- coding: utf-8 -*-
#
# File: XMLRPCServer.py
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
from Products.GoPantsPockets.RemoteQueryServer import RemoteQueryServer
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.GoPantsPockets.config import *

##code-section module-header #fill in your manual code here
import xmlrpclib
import urllib
import cPickle
from zLOG import LOG, INFO, WARNING, DEBUG, TRACE, PROBLEM, ERROR
##/code-section module-header

schema = Schema((

    StringField(
        name='baseURL',
        widget=StringField._properties['widget'](
            label='Baseurl',
            label_msgid='GoPantsPockets_label_baseURL',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

XMLRPCServer_schema = BaseFolderSchema.copy() + \
    getattr(RemoteQueryServer, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class XMLRPCServer(BaseFolder, RemoteQueryServer, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IXMLRPCServer)

    meta_type = 'XMLRPCServer'
    _at_rename_after_creation = True

    schema = XMLRPCServer_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('dispatchRemoteQuery')
    def dispatchRemoteQuery(self,userID,**kw):
        """
        """
        LOG('GoPantsPockets', DEBUG, "XMLRPCServer.dispatchRemoteQuery(userID=%s, **kw=%s)" % (repr(userID), repr(kw),))

        username = self.getUsername()
        password = self.getPassword()
        baseURL = self.getBaseURL()

        url_parts = urllib.splittype(baseURL)
        url = url_parts[0] + '://%s:%s@' % (username, password) + url_parts[1][2:] + '/portal_gopantspockets'
        LOG('GoPantsPockets', DEBUG, "Connecting to %s" % url) # Yes it shows the password in your logs.
        server = xmlrpclib.Server(url)

        columns = self.getColumnsOfInterest()

        # That's the core routine here. Note the trick where I pickle
        # the query into a string before I send it. I avoided a ton of
        # issues with datatypes that way.
        query = {'userID':userID, 'kw':kw, 'columns':columns}
        pickled_query = cPickle.dumps(query)
        try:
            pickled_cerebri = server.portal_gopantspockets.handleRemoteQuery(pickled_query)
        except xmlrpclib.ProtocolError, e:
            LOG('GoPantsPockets', ERROR, '%s %s' % (e.errcode, e.errmsg))
            raise e

        cerebri = cPickle.loads(pickled_cerebri)
        LOG('GoPantsPockets', DEBUG, "Got %d results" % len(cerebri))

        resultSet = [dict(cerebrum.items()) for cerebrum in cerebri]
        res = self.applyRewriteRules(resultSet)
        res = self.deduplicateResultSet(resultSet)

        for item in res:
            item['gopantspockets_metainfo']['permalink'] = self.getBaseURL()+"/resolveuid/"+item.get('UID')+"/view"

        return res

    security.declarePublic('setUsernameAndPassword')
    def setUsernameAndPassword(self):
        """
        """
        if not hasattr(self, 'username'):
            self.manage_addProperty('username', 'xmlrpc', 'string')
        if not hasattr(self, 'password'):
            self.manage_addProperty('password', '', 'string')
        self.REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_propertiesForm')
        return

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """
        infos = []
        infos.append("baseURL: %s" % self.getBaseURL())
        infos.append("username: %s" % self.getUsername())
        pwd = "password:"
        if self.getPassword():
            pwd += "*****"
        else:
            pwd += "-None-"
        infos.append(pwd)
        return " / ".join(infos)

    # Manually created methods

    def getUsername(self):
        if not hasattr(self, 'username'):
            self.manage_addProperty('username', 'xmlrpc', 'string')
        return self.username

    def getPassword(self):
        if not hasattr(self, 'password'):
            self.manage_addProperty('password', '', 'string')
        return self.password



registerType(XMLRPCServer, PROJECTNAME)
# end of class XMLRPCServer

##code-section module-footer #fill in your manual code here
##/code-section module-footer

