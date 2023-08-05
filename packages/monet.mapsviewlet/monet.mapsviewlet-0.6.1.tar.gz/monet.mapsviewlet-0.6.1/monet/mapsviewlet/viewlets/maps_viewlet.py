# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common

from monet.mapsviewlet.browser.maps_view import MapsView

from Products.Maps.interfaces import IGeoLocation
from Products.Maps import config

class GMapViewlet(common.ViewletBase, MapsView):
    """A viewlet for showing Google Maps on contents"""
    
    def __init__(self, context, request, view, manager):
        common.ViewletBase.__init__(self, context, request, view, manager)
        portal_props = getToolByName(context, 'portal_properties')
        self.properties = getattr(portal_props, config.PROPERTY_SHEET, None)

    render = ViewPageTemplateFile('gmaps.pt')

    def _search_key(self, property_id):
        """Stolen from Products.Maps (this time: really stolen!)"""

        if self.properties is None:
            return None
        keys_list = getattr(self.properties, property_id, None)
        if keys_list is None:
            return None
        keys = {}
        for key in keys_list:
            url, key = key.split('|')
            url = url.strip()
            # remove trailing slashes
            url = url.strip('/')
            key = key.strip()
            keys[url] = key
        portal_url_tool = getToolByName(self.context, 'portal_url')
        portal_url = portal_url_tool()
        portal_url = portal_url.split('/')
        while len(portal_url) > 2:
            url = '/'.join(portal_url)
            if keys.has_key(url):
                return keys[url]
            portal_url = portal_url[:-1]
        return None

    @property
    def googlemaps_key(self):
        return self._search_key(config.PROPERTY_GOOGLE_KEYS_FIELD)

    @memoize
    def getKmlRelated(self):
        """Get all related contents that lead to .kml files.
        @return: a list of URL to download those files.
        """
        try:
            related = self.context.getRelatedItems()
            related = ["%s/at_download/file" % x.absolute_url() for x in related if hasattr(x, 'getFilename') and x.getFilename().endswith(".kml")]
        except AttributeError:
            related = []
        return related

    @property
    def view_map(self):
        """Check if the current viewlet can display the map; same as "canShowMap" but also check is there is a location"""
        if self.canShowMap() and self.getMapLocation():
            return True
        return False

    def getSiteLanguage(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.language() or portal_state.default_language() or 'en'

    def getLocation(self):
        return self.context.getLocation()

    def getMapLocation(self):
        geolocation = IGeoLocation(self.context)
        return geolocation.getMapLocation()

    def getZoomLevel(self):
        context = self.context
        return context.getField('zoomLevel').get(context)

    def getPopupType(self):
        context = self.context
        return context.getField('markerTextSelection').get(context)
    
    def getPopupText(self):
        context = self.context
        return context.getField('markerText').get(context)

    def update(self):
        self.relatedKml = self.getKmlRelated()


