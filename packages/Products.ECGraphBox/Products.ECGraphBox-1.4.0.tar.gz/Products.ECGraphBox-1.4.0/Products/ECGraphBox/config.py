# -*- coding: utf-8 -*-
# $Id: config.py 1547 2011-04-01 07:34:35Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECGraphBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.
from Products.CMFCore import permissions
from Products.ATContentTypes.configuration.config import zconf

# load custom configuration from product ECAssignmentBox
try:
    from Products.ECAssignmentBox.config import *
except ImportError:
    pass


PROJECTNAME = "ECGraphBox"

PRODUCT_GLOBALS = globals()

# Dependend products - installed by quick-installer
DEPENDENCIES = ['ECAssignmentBox']

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []


# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"

permissions.setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

ADD_CONTENT_PERMISSIONS = {
    'ECGraphBox': 'ECGraphBox: Add ECGraphBox',
    'ECGraph': 'ECGraph: Add ECGraph',
}

permissions.setDefaultRoles('ECGraphBox: Add ECGraphBox', ('Manager','Owner'))
permissions.setDefaultRoles('ECGraph: Add ECGraph', ('Manager','Owner'))
