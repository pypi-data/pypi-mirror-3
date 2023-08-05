# -*- coding: utf-8 -*-

from zope import interface
from redturtle.smartlink.interfaces import ISmartLinked
from Products.CMFPlone.utils import getFSVersionTuple

def install(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-redturtle.smartlink:default')
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.smartlink:default')
    #if getFSVersionTuple()[0]>=4:
    #    unregisterIcon(portal)
    

def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-redturtle.smartlink:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.smartlink:uninstall')
    if getFSVersionTuple()[0]>=4:
        unregisterIcon(portal)
    if not reinstall:
        removeSmartLinkMarks(portal)


def removeSmartLinkMarks(portal):
    """Remove all Smart Link marker interfaces all around the site"""
    log = portal.plone_log
    catalog = portal.portal_catalog
    smartlinkeds = catalog(object_provides=ISmartLinked.__identifier__)

    log("Uninstall Smart Link: removing flag to internally linked contents...")
    for linked in smartlinkeds:
        content = linked.getObject()
        # Bee lazy, so use the already developed procedure for the delete-events
        unLink(portal, content)
        interface.noLongerProvides(content, ISmartLinked)
        content.reindexObject(['object_provides'])
        log("   unmarked %s" % '/'.join(content.getPhysicalPath()))
    log("...done. Thanks you for using me!")

    # TODO: the perfect world is the one where SmartLink(s) are converted back to ATLink(s)


def unLink(portal, object):
    """Remove the reference from the smart link and the object itself, changing the internal link to
    a normal external link.
    """
    reference_catalog = portal.reference_catalog
    backRefs = reference_catalog.getBackReferences(object, relationship='internal_page')
    for r in backRefs:
        r.setInternalLink(None)
        r.setExternalLink(object.absolute_url())
        r.reindexObject(['getRemoteUrl'])

def unregisterIcon(portal):
    """Remove icon expression from Link type"""
    log = portal.plone_log
    portal_types = portal.portal_types
    link = portal_types.getTypeInfo("Link")
    #link.icon_expr = ''
    link.content_icon = ''
    link.manage_changeProperties(content_icon='', icon_expr='')
    log("Removing icon type info")


