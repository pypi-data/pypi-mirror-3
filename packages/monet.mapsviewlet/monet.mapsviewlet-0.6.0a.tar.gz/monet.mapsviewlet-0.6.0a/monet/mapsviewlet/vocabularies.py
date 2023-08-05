# -*- coding: utf-8 -*-

try:
    from zope.app.schema.vocabulary import IVocabularyFactory
except ImportError:
    # Plone 4.1
    from zope.schema.interfaces import IVocabularyFactory

from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from monet.mapsviewlet import monetMessageFactory as _

class MarkerTextTypesVocabulary(object):
    """Vocabulary factory for all kind op baloon
    """
    implements( IVocabularyFactory )

    def __call__(self, context):
        return SimpleVocabulary([SimpleTerm('location',_(u'Location')),
                                 SimpleTerm('text',_(u'Custom text (see below)'))])

MarkerTextTypesVocabularyFactory = MarkerTextTypesVocabulary()