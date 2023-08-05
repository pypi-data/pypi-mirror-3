from plone.app.registry.browser import controlpanel

from collective.taghelper import taghelperMessageFactory as _
from collective.taghelper.interfaces import ITagHelperSettingsSchema



class TagHelperSettings(controlpanel.RegistryEditForm):
    #form_fields = form.FormFields(ITagHelperSettingsSchema)
    schema = ITagHelperSettingsSchema
    label = _(u'Tag Helper Settings')
    description = _(u'API Keys for the webservices used to extract terms')

    def updateFields(self):
        super(TagHelperSettings, self).updateFields()


    def updateWidgets(self):
        super(TagHelperSettings, self).updateWidgets()


class TagHelperSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TagHelperSettings



