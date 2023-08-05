import hashlib
from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ATContentTypes.interfaces.topic import IATTopic

from Products.googlecoop import googlecoopMessageFactory as _
from Products.googlecoop.interfaces import IGoogleCoopSettingsSchema

from utils import extract_urls

class ICseAnnotationsView(Interface):
    """
    CseAnnotations view interface
    """



class CseAnnotationsView(BrowserView):
    """
    CseAnnotations browser view
    """
    implements(ICseAnnotationsView)
    google_cse_id =''
    brains = []
    labelkeywords = False
    template = ViewPageTemplateFile('cseannotationsview.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IGoogleCoopSettingsSchema)
        identifier = self.settings.identifier
        if identifier:
            self.creator, self.google_cse_id = identifier.split(':')
        if IATTopic.providedBy(self.context):
            self.google_cse_id = hashlib.md5(self.context.UID()).hexdigest()
        self.labelkeywords= self.settings.labelkeywords

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def get_annotations(self):
        if IPloneSiteRoot.providedBy(self.context):
            brains = self.portal_catalog(portal_type = self.settings.cse_content_types)
        elif IATTopic.providedBy(self.context):
            brains = self.context.queryCatalog()
        urls = []
        for annotation in extract_urls(brains, ['Subject'], self.portal_catalog):
            if annotation['url'] in self.settings.exclude_domains:
                continue
            else:
                urls.append(annotation)
        return urls

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type','text/xml; charset=utf-8')
        return self.template()
