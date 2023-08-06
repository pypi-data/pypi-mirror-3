# -*- coding: utf-8 -*-
# $Id: setuphandlers.py 1549 2011-04-01 09:17:42Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECGraphBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import transaction
import logging
log = logging.getLogger('ECGraphBox: setuphandlers')

from Products.CMFCore.utils import getToolByName

from Products.ECGraphBox import config
from Products.ECGraphBox import LOG


def isNotECGraphBoxProfile(context):
    """Read marker file
    """
    return context.readDataFile("ECGraphBox_marker.txt") is None


def postInstall(context):
    """Called at the end of the setup process (the right place for 
    your custom code). 
    """
    
    if isNotECGraphBoxProfile(context): return 
    
    LOG.info('Post installation...')
    reindexIndexes(context)


def installGSDependencies(context):
    """Install dependend profiles.
    """

    if isNotECGraphBoxProfile(context): return 
    
    # Has to be refactored as soon as generic setup allows a more 
    # flexible way to handle dependencies.
    return


def installQIDependencies(context):
    """Install dependencies
    """

    if isNotECGraphBoxProfile(context): return 
    
    LOG.info("Installing QI dependencies...")

    site = context.getSite()

    portal = getToolByName(site, 'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    for dependency in config.DEPENDENCIES:
        if quickinstaller.isProductInstalled(dependency):
            LOG.info('Reinstalling dependency %s:' % dependency)
            quickinstaller.reinstallProducts([dependency])
            transaction.savepoint()
        else:
            LOG.info('Installing dependency %s:' % dependency)
            quickinstaller.installProduct(dependency)
            transaction.savepoint()

        #quickinstaller.installProduct(dependency)
        #transaction.savepoint() 


def reindexIndexes(context):
    """Reindex some indexes.

    Indexes that are added in the catalog.xml file get cleared
    everytime the GenericSetup profile is applied.  So we need to
    reindex them.

    Since we are forced to do that, we might as well make sure that
    these get reindexed in the correct order.
    """
    if isNotECGraphBoxProfile(context): return 

    site = context.getSite()

    pc = getToolByName(site, 'portal_catalog')
    indexes = [
        'isAssignmentBoxType',
        'isAssignmentType',
        'getRawAssignment_reference',
        'getRawRelatedItems',
        'review_state',
        ]

    # Don't reindex an index if it isn't actually in the catalog.
    # Should not happen, but cannot do any harm.
    ids = [id for id in indexes if id in pc.indexes()]
    if ids:
        pc.manage_reindexIndex(ids=ids)
    
    LOG.info('Reindexed %s' % indexes)
