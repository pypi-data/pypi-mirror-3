# -*- coding: utf-8 -*-
# $Id: ECAutoAssignment.py 1549 2011-04-01 09:17:42Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAutoAssessmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import re, time
import traceback
import logging

from types import BooleanType
from types import IntType

import interfaces

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager

from zope.interface import implements

from Products.Archetypes.atapi import *
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore.utils import getToolByName

from Products.ECAssignmentBox.content.ECAssignment import ECAssignment

from Products.ECGraphBox import config

# set max wait time; after a maxium of 15 tries we will give up getting 
# any result from the spooler until this assignment will be accessed again
MAX_WAIT_TIME = 15
MAX_SLEEP_TIME = 1.2

schema = Schema((

),
)

ECGraph_schema = ECAssignment.schema.copy() + \
    schema.copy()

class ECGraph(ECAssignment, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IECGraph)

    meta_type = 'ECG'
    _at_rename_after_creation = True

    schema = ECGraph_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods
    security.declarePublic('getGradeModeReadFieldNames')
    def getViewModeReadFieldNames(self):
        """
        Returns the names of the fields which are shown in view mode.
        This method should be overridden in subclasses which need more fields.

        @see ECAssignment#getViewModeReadFileNames
        @return list of field names
        """
        return ['remarks', 'feedback', 'mark']   

registerType(ECGraph, config.PROJECTNAME)
# end of class ECAutoAssignment
