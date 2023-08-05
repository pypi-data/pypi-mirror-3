# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.Maps.interfaces import IMarker

from monet.mapsviewlet.interfaces import ILocationProvider

class MonetGeoLocation(object):
    implements(IMarker)

    def __init__(self, context):
        self.context = context
        self.title = context.Title()
        self.description = context.Description()
        self.layers = None
        self.icon = None
        self.url = context.absolute_url()

    def getMapLocation(self):
        """Return a location info
        First check for the extender field "geolocation". If not found call for a location provider
        (that commonly is the location field of the content)
        """
        context = self.context
        try:
            map_default_location = getToolByName(context, 'portal_properties').maps_properties.map_default_location
        except AttributeError:
            map_default_location = '0.0, 0.0'
        coord = context.getField('geolocation').get(context)
        geolocation = "%s, %s" % (coord[0], coord[1])
        
        if not geolocation or geolocation==map_default_location:
            # not found any custom geolocation, call for a locationprovider
            # (commonly: take the location field)
            geolocation = ILocationProvider(self.context).getLocation()
        
        return geolocation

    @property
    def latitude(self):
        context = self.context
        coord = context.getField('geolocation').get(context)
        if coord[0]==0.0:
            return None
        return coord[0]

    @property
    def longitude(self):
        context = self.context
        coord = context.getField('geolocation').get(context)
        if coord[1]==0.0:
            return None
        return coord[1]

