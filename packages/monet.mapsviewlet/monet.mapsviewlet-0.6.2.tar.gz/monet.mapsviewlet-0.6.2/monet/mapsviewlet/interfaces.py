# -*- coding: utf-8 -*-

from zope.interface import Interface

class IMonetMapsLayer(Interface):
    """Interface for the product layer"""


class IMonetMapsEnabledContent(Interface):
    """Marker interface for content type enabled to use the Google Map"""


class ILocationProvider(Interface):
    """An object able to provide a location info"""
    
    def getLocation():
        """Get the location info string"""