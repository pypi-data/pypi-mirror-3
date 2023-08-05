from zope.component import getUtility

from plone.app.layout.viewlets import common as base
from plone.registry.interfaces import IRegistry

from Products.googlecoop.interfaces import IGoogleCoopSettingsSchema


class CoopJsHeadViewlet(base.ViewletBase):

    def update(self):
        try:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IGoogleCoopSettingsSchema)
            self.api_key = settings.googleapi
        except:
            self.api_key = ''

    def render(self):
        return '<script type="text/javascript" src="https://www.google.com/jsapi?%s"></script>' % self.api_key
