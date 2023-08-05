# -*- coding: utf-8 -*-

import unittest
from monet.mapsviewlet.tests import base

from zope.interface import alsoProvides
from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent

from Products.Maps.interfaces import IMarker

class TestProductsMapIntegration(base.FunctionalTestCase):

    def test_mapEnabledIsMarker(self):
        self.login('contributor1')
        page = self.createPage('p1')
        self.assertRaises(TypeError, IMarker, page)
        alsoProvides(page, IMonetMapsEnabledContent)
        self.assertTrue(IMarker(page))

    def test_monetMarker(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        marker = IMarker(page)
        self.assertEquals(marker.latitude, None)
        self.assertEquals(marker.longitude, None)
        page.getField('geolocation').set(page, (44.844, 12.113))
        marker = IMarker(page)
        self.assertEquals(marker.latitude, 44.844)
        self.assertEquals(marker.longitude, 12.113)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProductsMapIntegration))
    return suite