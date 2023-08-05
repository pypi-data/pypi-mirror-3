# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from AccessControl import Unauthorized

from zope import interface
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent
from monet.mapsviewlet import monetMessageFactory as _

class MapsView(BrowserView):
    """A public view to test maps functionality"""
    
    def _getUser(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state.member()
    
    def canEnable(self):
        """Test if the user can enable the map on the current content.
        You can't enable the viewlet if the content has no Location
        """
        context = self.context
        return self._getUser().has_permission('Enable Monet Googlemaps viewlet', self.context) \
                and not IMonetMapsEnabledContent.providedBy(context)
    
    def canDisable(self):
        """Check if the user can disable the map"""
        return self._getUser().has_permission('Enable Monet Googlemaps viewlet', self.context) and \
                IMonetMapsEnabledContent.providedBy(self.context)
    
    def enable(self):
        """Enable the map"""
        if not self.canEnable():
            raise Unauthorized("You can't enable the map for this content")
        context = self.context
        interface.directlyProvides(context, IMonetMapsEnabledContent)
        context.reindexObject(idxs=['object_provides',])
        putils = getToolByName(context, 'plone_utils')
        putils.addPortalMessage(_(u"Map enabled"))
        if not context.getLocation() and (context.getField('geolocation') and context.getField('geolocation').get(context)==(0, 0)):
            putils.addPortalMessage(_(u"The current content has no Location nor Geolocation infos; maps will not be show",),
                                    type='warning')
        self.request.response.redirect(context.absolute_url())

    def disable(self):
        """Disable the map"""
        if not self.canDisable():
            raise Unauthorized("You can't enable the map for this content")
        context = self.context
        interface.noLongerProvides(self.context, IMonetMapsEnabledContent)
        context.reindexObject(idxs=['object_provides',])
        putils = getToolByName(context, 'plone_utils')
        putils.addPortalMessage(_(u"Map disabled"))
        self.request.response.redirect(context.absolute_url())

    @memoize
    def canShowMap(self):
        """Return true if we are in the view of the content"""
        context = self.context
        context_state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        isViewTemplate = context_state.is_view_template()
        return isViewTemplate and IMonetMapsEnabledContent.providedBy(context)



