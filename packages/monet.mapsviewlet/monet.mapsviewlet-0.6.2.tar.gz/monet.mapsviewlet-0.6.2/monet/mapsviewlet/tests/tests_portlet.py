# -*- coding: utf-8 -*-

import unittest
from monet.mapsviewlet.tests import base

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from monet.mapsviewlet.portlets import kml 

class TestPortlet(base.FunctionalTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='kml.KmlControlsPortlet')
        self.assertEquals(portlet.addview,
                          'kml.KmlControlsPortlet')

    def test_interfaces(self):
        portlet = kml.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='kml.KmlControlsPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        #addview.createAndAdd(data={})
        addview()

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   kml.Assignment))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = kml.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, kml.Renderer))


class TestRenderer(base.FunctionalTestCase):

    def afterSetUp(self):
        super(TestRenderer, self).afterSetUp()
        self.login('contributor1')
        self.setRoles(('Manager', ))
        self.page = self.createPage('p1')
        self.goTo(self.page)

    def addRelated(self, content, *args):
        uids = []
        for x in args:
            self.portal.invokeFactory(id=x, type_name="File")
            f = self.portal[x]
            f.setTitle(x)
            f.setFilename(x)
            uids.append(f.UID())
        content.setRelatedItems(uids)

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.page
        request = self.request
        view = view or self.page.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment
        # constructor.
        assignment = assignment or kml.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def getPortletRenderer(self):
        r = self.renderer(context=self.page,
                          assignment=kml.Assignment())
        r = r.__of__(self.page)
        r.update()
        return r

    def test_hideWhenNoRelated(self):
        r = self.getPortletRenderer()
        self.assertFalse(r.available)

    def test_hideWhenRelatedNotKML(self):
        self.addRelated(self.page, 'manual.doc')
        r = self.getPortletRenderer()
        self.assertFalse(r.available)

    def test_showWhenHaveRelatedKML(self):
        self.addRelated(self.page, 'file1.kml', 'manual.doc')
        r = self.getPortletRenderer()
        self.assertTrue(r.available)
        
    def test_showOnlyKMLInPortlet(self):
        self.addRelated(self.page, 'file1.kml', 'manual.doc', 'file3.kml')
        r = self.getPortletRenderer()
        output = r.render()
        self.assertTrue('file1.kml' in output)
        self.assertFalse('manual.doc' in output)
        self.assertTrue('file3.kml' in output)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortlet))
    suite.addTest(unittest.makeSuite(TestRenderer))
    return suite

