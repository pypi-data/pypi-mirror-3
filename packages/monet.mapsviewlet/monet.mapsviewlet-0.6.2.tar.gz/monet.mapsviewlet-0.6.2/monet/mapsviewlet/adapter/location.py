# -*- coding: utf-8 -*-

from zope.interface import implements
from monet.mapsviewlet.interfaces import ILocationProvider

class ATLocationProvider(object):
    """Basic location provider for Archetypes: return the location field value"""
    implements(ILocationProvider)
    
    def __init__(self, context):
        self.context = context
    
    def getLocation(self):
        return self.context.getLocation() 