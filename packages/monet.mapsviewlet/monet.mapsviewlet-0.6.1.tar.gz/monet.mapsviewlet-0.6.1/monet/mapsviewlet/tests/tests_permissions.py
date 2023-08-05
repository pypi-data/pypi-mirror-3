# -*- coding: utf-8 -*-

import unittest
from monet.mapsviewlet.tests import base
from AccessControl import Unauthorized 

from zope.interface import alsoProvides
from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent

class TestPermissions(base.FunctionalTestCase):

    def test_ownerCanEnableMap(self):
        self.login('contributor1')
        page = self.createPage('p1')
        self.assertTrue(self.getMember().has_permission('Enable Monet Googlemaps viewlet', page))
        self.assertTrue(page.restrictedTraverse('@@monet.gmap').canEnable())
        self.assertFalse(IMonetMapsEnabledContent.providedBy(page))        

    def test_otherCantEnableMap(self):
        self.login('contributor1')
        page = self.createPage('p1')
        self.logout()
        self.login('contributor2')
        self.assertFalse(self.getMember().has_permission('Enable Monet Googlemaps viewlet', page))
        self.assertFalse(page.restrictedTraverse('@@monet.gmap').canEnable())

    def test_ownerCanDisableMap(self):
        self.login('contributor1')
        page = self.createPage('p1')
        page.restrictedTraverse('@@monet.gmap').enable()
        self.assertTrue(IMonetMapsEnabledContent.providedBy(page))
        self.assertTrue(self.getMember().has_permission('Enable Monet Googlemaps viewlet', page))
        self.assertFalse(page.restrictedTraverse('@@monet.gmap').canEnable())
        self.assertTrue(page.restrictedTraverse('@@monet.gmap').canDisable())

    def test_otherCantDisableMap(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        self.logout()
        self.login('contributor2')
        self.assertFalse(page.restrictedTraverse('@@monet.gmap').canEnable())
        self.assertFalse(page.restrictedTraverse('@@monet.gmap').canDisable())
        
    def test_cantDoubleEnableMap(self):
        self.login('contributor1')
        page = self.createPage('p1')
        alsoProvides(page, IMonetMapsEnabledContent)
        self.assertRaises(Unauthorized, page.restrictedTraverse('@@monet.gmap').enable)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPermissions))
    return suite