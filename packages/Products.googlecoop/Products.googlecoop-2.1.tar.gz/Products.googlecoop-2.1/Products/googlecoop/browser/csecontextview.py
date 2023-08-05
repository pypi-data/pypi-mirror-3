import hashlib
from zope.interface import implements, Interface
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ATContentTypes.interfaces.topic import IATTopic

from Products.googlecoop.interfaces import IGoogleCoopSettingsSchema
from Products.googlecoop import googlecoopMessageFactory as _

from utils import extract_labels

class ICseContextView(Interface):
    """
    CseContext view interface
    """


class CseContextView(BrowserView):
    """
    CseContext browser view
    """
    implements(ICseContextView)

    template = ViewPageTemplateFile('csecontextview.pt')

    google_cse_id =''
    creator =''
    keywords = ''
    enable_suggest = ''
    ad_status = 'false'
    labelkeywords = False
    brains = []

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IGoogleCoopSettingsSchema)

    @property
    def mtool(self):
        return getToolByName(self.context, 'portal_membership')


    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def language(self):
        """
        @return: Two letter string, the active language code
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                        name=u'plone_portal_state')
        current_language = portal_state.language()
        return current_language

    def get_labels(self):
        return extract_labels(self.brains, ['Subject'], self.portal_catalog)

    def __call__(self):
        if IPloneSiteRoot.providedBy(self.context):
            self.brains = self.portal_catalog(portal_type = self.settings.cse_content_types)
            identifier = self.settings.identifier
            if identifier:
                self.creator, self.google_cse_id = identifier.split(':')
        elif IATTopic.providedBy(self.context):
            self.brains = self.context.queryCatalog()
            creator = self.context.Creator()
            cemail = self.mtool.getMemberById(creator).getProperty('email', None)
            if cemail:
                self.creator = hashlib.sha1('mailto:' +
                        cemail.strip().lower()).hexdigest()
            else:
                self.creator = hashlib.sha1('mailto:' +
                        creator.lower()).hexdigest()
            self.google_cse_id = hashlib.md5(self.context.UID()).hexdigest()
        self.enable_suggest = str(self.settings.autocomplete).lower()
        self.ad_status = str(self.settings.adstatus).lower()
        self.labelkeywords= self.settings.labelkeywords
        self.request.RESPONSE.setHeader('Content-Type','text/xml; charset=utf-8')
        return self.template()


