# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2012 by Georg Gogo. BERNHARD <gogo@bluedynamics.com>
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Georg Gogo. BERNHARD <gogo@bluedynamics.com>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('GoPantsPockets: setuphandlers')
from Products.GoPantsPockets.config import PROJECTNAME
from Products.GoPantsPockets.config import DEPENDENCIES
import os
from config import product_globals
from Globals import package_home
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotGoPantsPocketsProfile(context):
    return context.readDataFile("GoPantsPockets_marker.txt") is None

def setupHideToolsFromNavigation(context):
    """hide tools"""
    if isNotGoPantsPocketsProfile(context): return
    # uncatalog tools
    site = context.getSite()
    toolnames = ['portal_gopantspockets']
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
        for toolname in toolnames:
            try:
                portal[toolname].unindexObject()
            except:
                pass
            current = list(navtreeProperties.getProperty('idsNotToList') or [])
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)

def installRelations(context):
    """imports the relations.xml file"""
    if isNotGoPantsPocketsProfile(context): return
    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    if not qi.isProductInstalled('Relations'):
        # you can't declare relations unless you first install the Relations product
        logger.info("Installing Relations Product")
        qi.installProducts(['Relations'])
    relations_tool = getToolByName(site, 'relations_library')
    xmlpath = os.path.join(package_home(product_globals), 'data',
                           'relations.xml')
    f = open(xmlpath)
    xml = f.read()
    f.close()
    relations_tool.importXML(xml)



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotGoPantsPocketsProfile(context): return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotGoPantsPocketsProfile(context): return
    site = context.getSite()



##code-section FOOT
##/code-section FOOT
