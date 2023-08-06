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


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
##/code-section config-head


PROJECTNAME = "GoPantsPockets"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))
ADD_CONTENT_PERMISSIONS = {
    'StoredQuery': 'GoPantsPockets: Add StoredQuery',
    'XMLRPCServer': 'GoPantsPockets: Add XMLRPCServer',
    'KeyValuePair': 'GoPantsPockets: Add KeyValuePair',
    'RewriteRule': 'GoPantsPockets: Add RewriteRule',
    'SortRule': 'GoPantsPockets: Add SortRule',
    'RESTServer': 'GoPantsPockets: Add RESTServer',
    'LocalInstance': 'GoPantsPockets: Add LocalInstance',
    'RemoteQueryServer': 'GoPantsPockets: Add RemoteQueryServer',
    'InteractiveInput': 'GoPantsPockets: Add InteractiveInput',
    'gopantspockets_page': 'GoPantsPockets: Add gopantspockets_page',
    'QueryParameters': 'GoPantsPockets: Add QueryParameters',
}

setDefaultRoles('GoPantsPockets: Add StoredQuery', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add XMLRPCServer', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add KeyValuePair', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add RewriteRule', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add SortRule', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add RESTServer', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add LocalInstance', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add RemoteQueryServer', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add InteractiveInput', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add gopantspockets_page', ('Manager','Owner'))
setDefaultRoles('GoPantsPockets: Add QueryParameters', ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.GoPantsPockets.AppConfig import *
except ImportError:
    pass
