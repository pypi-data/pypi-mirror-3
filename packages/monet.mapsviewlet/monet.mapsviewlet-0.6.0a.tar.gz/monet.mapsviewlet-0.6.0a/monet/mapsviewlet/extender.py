# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.configuration import zconf
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from monet.mapsviewlet import monetMessageFactory as _
from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent

from Products.Maps.field import LocationWidget, LocationField

class ExtensionLocationField(ExtensionField, LocationField):
    """ derivative of Products.Maps LocationField for extending schemas """

class ExtensionIntegerField(ExtensionField, atapi.IntegerField):
    """ derivate from Archetypes basic IntegerField """

class ExtensionTextField(ExtensionField, atapi.TextField):
    """ derivate from Archetypes basic TextField """

class ExtensionStringField(ExtensionField, atapi.StringField):
    """ derivate from Archetypes basic StringField """

class MonetMapsExtender(object):
    adapts(IMonetMapsEnabledContent)
    implements(ISchemaExtender)

    fields = [
        ExtensionLocationField('geolocation',
                  required=False,
                  searchable=False,
                  validators=('isGeoLocation',),
                  schemata='Geolocation',
                  widget = LocationWidget(
                        label = _(u'Detailed geolocation'),
                        description = _('help_geolocation',
                                        default=u"Use this field if you want that the map point onto a place "
                                                u"different from the default Location ones.\n"
                                                u"This can be useful if you want to keep a general location on"
                                                u"the Location field, but move the marker somewhere else."),
                  ),
        ),
        ExtensionIntegerField('zoomLevel',
                  required=True,
                  validators=('isInt',),
                  schemata='Geolocation',
                  default=15,
                  widget = atapi.IntegerWidget(
                        label = _(u'Starting zoom level'),
                        description = _('help_zoomLevel',
                                        default=u"This value is the default zoom level on the map"
                                        ),
                  ),
        ),
        ExtensionStringField('markerTextSelection',
                  required=True,
                  schemata='Geolocation',
                  default="location",
                  enfoceVocabulary=True,
                  vocabulary_factory='monet.mapsviewlet.vocabulary.markerTextTypes',
                  widget = atapi.SelectionWidget(
                            label = _(u'Information to display in the marker'),
                  ),
        ),
        ExtensionTextField('markerText',
                  required=False,
                  validators = ('isTidyHtmlWithCleanup',),
                  schemata='Geolocation',
                  default_output_type = 'text/x-html-safe',
                  widget = atapi.RichWidget(
                            label = _(u'Text in the marker'),
                            description = _('help_markerText',
                                            default=u'You can provide there an alternative custom text to be shown in the marker.\n'
                                                    u"Leave empty if you don't want to display the popup text at all."),
                            rows = 25,
                            allow_file_upload = zconf.ATDocument.allow_document_upload,
                  ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

