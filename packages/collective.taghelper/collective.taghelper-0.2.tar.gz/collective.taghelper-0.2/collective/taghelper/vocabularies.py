from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.taghelper.interfaces import ITagHelperSettingsSchema


def tagging_vocabulary_factory(context):
    items = []
    items.append(('ttn', u'TagThe.Net'))
    try:
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITagHelperSettingsSchema)
        if settings.alchemy_api_key:
            items.append(('alchemy', u'AlchemyAPI'))
        if settings.yahoo_api_key:
            items.append(('yahoo', u'Yahoo'))
        if settings.calais_api_key:
            items.append(('calais', u'Open Calais'))
        if settings.silcc_url:
            items.append(('silcc', u'SiLLC'))
    except KeyError:
        return SimpleVocabulary.fromItems([])
    return SimpleVocabulary.fromItems(items)
