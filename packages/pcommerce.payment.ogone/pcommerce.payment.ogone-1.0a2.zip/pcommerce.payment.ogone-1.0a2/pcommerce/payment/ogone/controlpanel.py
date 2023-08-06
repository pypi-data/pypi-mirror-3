from plone.app.registry.browser import controlpanel
from pcommerce.payment.ogone import MessageFactory as _
from interfaces import IOgoneSettings


class OgoneSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IOgoneSettings
    label = _(u"Ogone PCommerce settings")
    description = _(u"The Ogone settings for PCOmmerce")

    def updateFields(self):
        super(OgoneSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(OgoneSettingsEditForm, self).updateWidgets()


class OgoneSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = OgoneSettingsEditForm
