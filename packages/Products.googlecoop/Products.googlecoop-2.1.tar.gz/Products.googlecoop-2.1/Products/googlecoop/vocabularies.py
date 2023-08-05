from zope.interface import implements
from zope.schema import vocabulary
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from Products.googlecoop.interfaces import IGoogleCoopSettingsSchema
from Products.googlecoop.browser.utils import extract_urls

class BaseVocabulary(object):
    implements(IVocabularyFactory)
    terms = []

    def __call__(self, context):
        terms = []
        for term in self.terms:
            terms.append(vocabulary.SimpleVocabulary.createTerm(term[0],
                                                                term[0],
                                                                term[1]))

        return vocabulary.SimpleVocabulary(terms)

class ShowAdsVocabulary(BaseVocabulary):
    terms = [
        (u'FORID:9', u'Right'),
        (u'FORID:10', u'Top and Right'),
        (u'FORID:11', u'Top and Bottom'),
        ]


class ExcludeDomainsVocabulary(BaseVocabulary):

    def __call__(self, context):
        try:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IGoogleCoopSettingsSchema)
            portal_catalog = getToolByName(registry.getParentNode(), 'portal_catalog')
            brains = portal_catalog(portal_type = settings.cse_content_types)
            self.terms = [(anno['url'],anno['url']) for anno in extract_urls(brains, [], portal_catalog)]
            self.terms.sort()
        except KeyError:
            pass
        return super(ExcludeDomainsVocabulary, self).__call__(context)
