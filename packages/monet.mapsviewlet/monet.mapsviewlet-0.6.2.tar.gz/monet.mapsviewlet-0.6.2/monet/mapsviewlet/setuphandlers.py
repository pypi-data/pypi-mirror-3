# -*- coding: utf-8 -*-

import logging
from zope.interface import noLongerProvides
from Products.CMFCore.utils import getToolByName
from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent

def setupVarious(context):
    if context.readDataFile('monet.mapsviewlet_various.txt') is None: 
        return

    #site = context.getSite()
    # nothing to do


def removeMarkers(context):
    if context.readDataFile('monet.mapsviewlet_uninstall.txt') is None: 
        return
    logger = logging.getLogger('monet.mapsviewlet')
    logger.info('Removing Monet Maps Viewlet interfaces from contents')
    site = context.getSite()
    catalog = site.portal_catalog
    mapped = catalog.unrestrictedSearchResults(object_provides=IMonetMapsEnabledContent.__identifier__)
    cnt = 0
    for brain in mapped:
        cnt+=1
        obj = brain.getObject()
        noLongerProvides(obj, IMonetMapsEnabledContent)
        obj.reindexObject(idxs=['object_provides',])
        logger.info('   removed from %s' % obj.absolute_url_path())
        # BBB - need also to remove schemaextender stuff?
    logger.info('Done (%s removed)' % cnt)


def migrateTo060(context):
    logger = logging.getLogger('monet.mapsviewlet')
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-monet.mapsviewlet:default')
    try:
        maps_properties = context.portal_properties.maps_properties
        maps_dict = dict([(x.split('|')[0].strip(), x.split('|')[1].strip()) for x in maps_properties.map_google_api_keys])
        monet_properties = context.portal_properties.monet_properties
        tobeadded = {}
        for conf in monet_properties.googlemaps_key:
            url, key = conf.split('|')[0].strip(), conf.split('|')[1].strip() 
            if url not in maps_dict.keys():
                tobeadded[url]=key
                logger.info("Key for %s must be migrated to Maps configuration" % url)

        if tobeadded:
            maps_dict.update(tobeadded)
            maps_properties.manage_changeProperties(map_google_api_keys=["%s | %s" % (x,maps_dict[x]) for x in maps_dict])
            logger.info("Migrated Google API keys")
        context.portal_properties.manage_delObjects(ids=['monet_properties',])
        logger.info("Removed deprecated monet_properties propertysheet")
    except AttributeError:
        pass
    logger.info("Migrated to 0.6.0")


def migrateTo061(context):
    logger = logging.getLogger('monet.mapsviewlet')
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile('profile-monet.mapsviewlet:default', 'actions')
    logger.info("Migrated to 0.6.1")

