# -*- coding: utf-8 -*-
#
# File: RESTServer.py
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
from Products.GoPantsPockets.RemoteQueryServer import RemoteQueryServer
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.GoPantsPockets.config import *

##code-section module-header #fill in your manual code here
import os
import xml2dict
import lxml.etree as ElementTree
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
    StringField(
        name='baseXPath',
        widget=StringField._properties['widget'](
            description="e.g. orgUnit/*/course",
            label='Basexpath',
            label_msgid='GoPantsPockets_label_baseXPath',
            description_msgid='GoPantsPockets_help_baseXPath',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),
    LinesField(
        name='allowedKWs',
        widget=LinesField._properties['widget'](
            description="e.g. token, orgUnitID, teachingTerm, language. Only the keywords given here will be transmitted. (Leave blank to send all keywords.)",
            label='Allowedkws',
            label_msgid='GoPantsPockets_label_allowedKWs',
            description_msgid='GoPantsPockets_help_allowedKWs',
            i18n_domain='GoPantsPockets',
        ),
        write_permission="Manage portal",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

RESTServer_schema = BaseFolderSchema.copy() + \
    getattr(RemoteQueryServer, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class RESTServer(BaseFolder, RemoteQueryServer, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IRESTServer)

    meta_type = 'RESTServer'
    _at_rename_after_creation = True

    schema = RESTServer_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('dispatchRemoteQuery')
    def dispatchRemoteQuery(self,userID,**kw):
        """
        """

        # print "GoPantsPockets:RESTServer.dipatchRemoteQuery kw=", repr(kw)

        allowed_kws = self.getAllowedKWs()
        if allowed_kws:
            kw = dict([k for k in kw.items() if k[0] in allowed_kws])

        baseURL = self.getBaseURL()
        params = "&".join([str(k)+"="+str(v) for k,v in kw.items()])
        if params:
            query_url = baseURL + "?" + params
        else:
            query_url = baseURL

        data = self.retrievedata(query_url)

        try:
            xmltree = ElementTree.XML(data)
        except:
            LOG("GoPantsPockets:RESTServer.dispatchRemoteQuery", WARNING, "XML could not be parsed")
            return []

        # print ElementTree.dump(xmltree) # @@@ Gogo.

        baseXPath=self.getBaseXPath() # orgUnit/orgUnit/course
        if not baseXPath:
            LOG("GoPantsPockets:RESTServer", ERROR, "No XPath given.")
            raise 'ERROR: GoPantsPockets:RESTServer "No XPath given."'

        # ElementTree.dump(xmltree)
        # import pdb;pdb.set_trace()

        items = xmltree.findall(baseXPath)

        # print "Found %d items." % (len(items),) # @@@ Gogo.

        resultSet = [dict(xml2dict.XmlDictConfig(item)) for item in items]

        res = self.applyRewriteRules(resultSet)
        res = self.deduplicateResultSet(resultSet)

        # print repr(res) # @@@ Gogo.

        return res

    security.declarePublic('getInfo')
    def getInfo(self):
        """
        """
        infos = []
        infos.append("baseURL: %s" % self.getBaseURL())
        infos.append("baseXPath: %s" % self.getBaseXPath())
        infos.append("allowedKWs: %s" % repr(self.getAllowedKWs()))
        s = " / ".join(infos)
        return s

    # Manually created methods

    def retrievedata(self, url):
        #
        # Usually I would like to access REST Services like this:
        #
        # import urllib2
        # u = urllib2.urlopen("https://campus.akbild.ac.at/akbild_onlinej/ws/webservice_v1.0/cdm/organization/courses/xml?token=...&orgUnitID=1&teachingTerm=&language=")
        # s = u.read()
        #
        # But our Oracle SSL just won't work wirh urllib2, so I use curl and
        # these parameters to make it use ssl version 2. If you are unhappy
        # please code a customisation for urllib2...
        #

        url.replace('&amp;','&')
        syscall = 'curl -2 -k "%s"' % url
        LOG("GoPantsPockets:RESTServer", DEBUG, "Performing system call %s." % repr(syscall))
        print "GoPantsPockets:RESTServer", DEBUG, "Performing system call %s." % repr(syscall)
        proc=os.popen(syscall)
        res=proc.read()
        return res



registerType(RESTServer, PROJECTNAME)
# end of class RESTServer

##code-section module-footer #fill in your manual code here
##/code-section module-footer

