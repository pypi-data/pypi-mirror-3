# -*- coding: utf-8 -*-

import unittest
from monet.mapsviewlet.tests import base

from zope.interface import alsoProvides
from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent

class TestMap(base.FunctionalTestCase):
    
    def test_fieldAddedToContent(self):
        self.login('contributor1')
        page = self.createPage('p1')
        self.assertFalse(page.getField('geolocation'))
        self.assertFalse(page.getField('zoomLevel'))
        self.assertFalse(page.getField('markerTextSelection'))
        self.assertFalse(page.getField('markerText'))
        page.restrictedTraverse('@@monet.gmap').enable()
        self.assertTrue(page.getField('geolocation'))
        self.assertTrue(page.getField('zoomLevel'))
        self.assertTrue(page.getField('markerTextSelection'))
        self.assertTrue(page.getField('markerText'))

    def test_emptyMessage(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        self.assertTrue('Map will be show here. Right now no geolocation infos has been provided to this content.' in page())
        
    def test_emptyMessageNotForAll(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        self.logout()
        self.login('contributor2')
        self.assertFalse('Map will be show here. Right now no geolocation infos has been provided to this content.' in page())

    def test_mapIsVisibleForOwner(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        page.setLocation('foo address')
        self.goTo(page)
        self.assertTrue('<div id="googlemaps">' in page())

    def test_mapIsVisibleForOther(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        page.setLocation('foo address')
        self.logout()
        self.goTo(page)
        self.assertTrue('<div id="googlemaps">' in page())

    def test_getMapLocationSimple(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        page.setLocation('foo address')
        self.goTo(page)
        self.assertTrue('<span style="display:none" id="gmaps-location">foo address</span>' in page())
        self.assertTrue('<span style="display:none" id="gmaps-official-location">foo address</span>' in page())

    def test_getMapLocationBoth(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        page.setLocation('foo address')
        page.getField('geolocation').set(page, (44.844, 12.113))
        self.goTo(page)
        self.assertTrue('<span style="display:none" id="gmaps-location">44.844, 12.113</span>' in page())
        self.assertTrue('<span style="display:none" id="gmaps-official-location">foo address</span>' in page())

    def test_getMapLocationGeolocationOnly(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        page.getField('geolocation').set(page, (44.844, 12.113))
        self.goTo(page)
        self.assertTrue('<span style="display:none" id="gmaps-location">44.844, 12.113</span>' in page())
        self.assertTrue('<span style="display:none" id="gmaps-official-location"></span>' in page())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMap))
    return suite