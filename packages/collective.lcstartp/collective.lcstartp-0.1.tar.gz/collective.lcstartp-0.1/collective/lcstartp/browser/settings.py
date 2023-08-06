from plone.app.registry.browser import controlpanel

from collective.lcstartp import lcStartPageMessageFactory as _
from collective.lcstartp.interfaces import ILcStartPageSettingsSchema

class LcStartPageSettings(controlpanel.RegistryEditForm):
    schema = ILcStartPageSettingsSchema
    label = _(u'LinkChecker start page Settings')
    description = _(u'LinkChecker start page  Settings')

    def updateFields(self):
        super(LcStartPageSettings, self).updateFields()


    def updateWidgets(self):
        super(LcStartPageSettings, self).updateWidgets()


class LcStartPageSettingsSchemaControlPanel(controlpanel.ControlPanelFormWrapper):
    form = LcStartPageSettings
