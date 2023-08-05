from plone.app.registry.browser import controlpanel

from Products.googlecoop import googlecoopMessageFactory as _
from Products.googlecoop.interfaces import IGoogleCoopSettingsSchema

class GoogleCoopSettings(controlpanel.RegistryEditForm):
    schema = IGoogleCoopSettingsSchema
    label = _(u'Google CSE Settings')
    description = _(u'Google Custom Search Settings')

    def updateFields(self):
        super(GoogleCoopSettings, self).updateFields()


    def updateWidgets(self):
        super(GoogleCoopSettings, self).updateWidgets()


class GoogleCoopSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = GoogleCoopSettings

