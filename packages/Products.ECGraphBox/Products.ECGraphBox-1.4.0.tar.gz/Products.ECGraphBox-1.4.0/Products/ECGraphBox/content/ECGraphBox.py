# -*- coding: utf-8 -*-
# $Id: ECAutoAssessmentBox.py 1549 2011-04-01 09:17:42Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAutoAssessmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import interfaces

from Acquisition import aq_inner

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope import interface
from zope.interface import implements

from Products.Archetypes.interfaces import IMultiPageSchema
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from Products.ECAssignmentBox.content.ECAssignmentBox import ECAssignmentBox
from Products.ECAssignmentBox.content.ECAssignmentBox import ECAssignmentBox_schema
#from Products.ECAssignmentBox import permissions

#from Products.ECAutoAssessmentBox.content.ECAutoAssignment import ECAutoAssignment
#from Products.ECAutoAssessmentBox.content.DynamicDataField import DynamicDataField
#from Products.ECAutoAssessmentBox.content.DynamicDataWidget import DynamicDataWidget

from Products.ECGraphBox import config

schema = Schema((

),
)

ECGraphBox_schema = ECAssignmentBox_schema.copy() + \
    schema.copy()

ECGraphBox_schema['id'].widget.visible = dict(edit=0, view=0)


class ECGraphBox(ECAssignmentBox):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IECGraphBox)

    meta_type = 'ECGB'
    _at_rename_after_creation = True

    schema = ECGraphBox_schema

    ##code-section class-header #fill in your manual code here

    # FIXME: allowed_content_types is defined in profile.default.types.ECAutoAssessmentBox.xml
    #        and should be used elsewhere
    allowed_content_types = ['ECG']
    
    # Methods


registerType(ECGraphBox, config.PROJECTNAME)
