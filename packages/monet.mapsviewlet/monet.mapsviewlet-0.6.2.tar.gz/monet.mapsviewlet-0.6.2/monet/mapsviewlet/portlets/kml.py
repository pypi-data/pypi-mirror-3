# -*- coding: utf-8 -*-

from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from monet.mapsviewlet import monetMessageFactory as _

class IKmlControlsPortlet(IPortletDataProvider):
    """Interface for handle KML portlet"""

class Assignment(base.Assignment):
    implements(IKmlControlsPortlet)

    @property
    def title(self):
        return _(u"KML map controls")

class Renderer(base.Renderer):

    render = ViewPageTemplateFile('kml_controls.pt')

    @property
    def available(self):
        return bool(self.kmls)

    @property
    @memoize
    def kmls(self):
        """List of all KML files"""
        try:
            kmls = self.context.getRelatedItems()
            kmls = [x.Title() for x in kmls if hasattr(x, 'getFilename') and x.getFilename().endswith(".kml")]
        except AttributeError:
            kmls = []
        return kmls

class AddForm(base.NullAddForm):
    label = _(u"Add KML controls")
    description = _("Add a portlet to manage KML data used from the Google Maps.")

    def create(self):
        assignment = Assignment()
        return assignment
