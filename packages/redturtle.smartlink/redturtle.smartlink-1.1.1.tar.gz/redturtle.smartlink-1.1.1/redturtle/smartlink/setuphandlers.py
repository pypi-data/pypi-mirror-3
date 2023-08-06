# -*- coding: utf-8 -*-

from redturtle.smartlink import logger
from Products.CMFCore.utils import getToolByName

PROFILE_ID = 'profile-redturtle.smartlink:default'

def setupVarious(context):
    portal = context.getSite()

    if context.readDataFile('redturtle.smartlink_various.txt') is None:
        return


def atLinkToSmartLink(context):
    portal = context.getSite()

    if context.readDataFile('redturtle.smartlink_linkToSmartLink.txt') is None:
        return
    
    try:
        from redturtle.smartlink.migrator import migrateLinkToSmartLink
        logger.info("Starting migration of ATLink to Smart Link")
        messages = migrateLinkToSmartLink(portal)
        for m in messages:
            logger.info(m)
        logger.info("Done")

    except ImportError:
        logger.error("Can't do anything. Check if Products.contentmigration is installed")


def smartLinkToATLink(context):
    portal = context.getSite()

    if context.readDataFile('redturtle.smartlink_smartLinkToATLink.txt') is None:
        return
    
    try:
        from redturtle.smartlink.migrator import migrateSmartLinkToLink
        logger.info("Starting migration of Smart Link to ATLink")
        messages = migrateSmartLinkToLink(portal)
        for m in messages:
            logger.info(m)
        logger.info("Done")

    except ImportError:
        logger.error("Can't do anything. Check if Products.contentmigration is installed")


def migrateTo1002(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'rolemap')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'controlpanel')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'action-icons')
    logger.info("Migrated to 1.1.0")

