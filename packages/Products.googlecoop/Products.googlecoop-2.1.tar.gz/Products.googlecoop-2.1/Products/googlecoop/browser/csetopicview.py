from zope.interface import implements, Interface
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from Products.googlecoop import googlecoopMessageFactory as _
from Products.googlecoop.interfaces import IGoogleCoopSettingsSchema

class ICseTopicView(Interface):
    """
    CseTopic view interface
    """



class CseTopicView(BrowserView):
    """
    CseTopic browser view
    """
    implements(ICseTopicView)

    js_template = """
      google.load('search', '1', {language : '%(lang)s'});
      google.setOnLoadCallback(function() {
        var customSearchControl = new google.search.CustomSearchControl(
            {'crefUrl' : '%(cref_url)s'});
        customSearchControl.setResultSetSize(google.search.Search.LARGE_RESULTSET);
        var options = new google.search.DrawOptions();
        options.setAutoComplete(%(autocomplete)s);
        customSearchControl.draw('google-coop-cse');
        customSearchControl.execute('%(searchtext)s');
      }, true);
    """


    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')()

    def language(self):
        """
        @return: Two letter string, the active language code
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                        name=u'plone_portal_state')
        current_language = portal_state.language()
        return current_language

    def get_js(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IGoogleCoopSettingsSchema)
        cseurl = '%s/csecontext.xml' % self.context.absolute_url()
        autocomplete = str(settings.autocomplete).lower()
        nocss = str(settings.nocss).lower()
        searchtext = self.request.form.get('SearchableText', '')
        return self.js_template % {'lang': self.language(),
                    'cref_url': cseurl,
                    'autocomplete': autocomplete,
                    'nocss': nocss,
                    'searchtext': searchtext }

