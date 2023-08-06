# -*- coding: utf-8 -*-
#
# File: IRemoteQueryServer.py
#
# Copyright (c) 2012 by Georg Gogo. BERNHARD <gogo@bluedynamics.com>
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Georg Gogo. BERNHARD <gogo@bluedynamics.com>"""
__docformat__ = 'plaintext'

from zope.interface import implements

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget

from zope.interface import Interface

class IRemoteQueryServer(Interface):
    """
    """
    ##code-section class-header_IRemoteQueryServer #fill in your manual code here
    ##/code-section class-header_IRemoteQueryServer

    def dispatchRemoteQuery(userID, **kw):
        """
        """

    def getInfo():
        """
        """

