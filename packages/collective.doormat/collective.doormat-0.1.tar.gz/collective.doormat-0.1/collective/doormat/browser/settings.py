from plone.app.registry.browser import controlpanel

from collective.doormat import doormatMessageFactory as _
from collective.doormat.interfaces import IDoormatSettingsSchema
#from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget as WYSIWYGWidget
from zope.formlib import form


class DoormatSettings(controlpanel.RegistryEditForm):
    #form_fields = form.FormFields(ITagHelperSettingsSchema)
    schema = IDoormatSettingsSchema
    label = _(u'Doormat Settings')
    description = _(u'Design you doormat')

    def updateFields(self):
        super(DoormatSettings, self).updateFields()
        self.fields['doormat_header'].widgetFactory = WYSIWYGWidget
        self.fields['doormat_footer'].widgetFactory = WYSIWYGWidget
        self.fields['section1_text'].widgetFactory = WYSIWYGWidget
        self.fields['section2_text'].widgetFactory = WYSIWYGWidget
        self.fields['section3_text'].widgetFactory = WYSIWYGWidget
        self.fields['section4_text'].widgetFactory = WYSIWYGWidget
        self.fields['section5_text'].widgetFactory = WYSIWYGWidget
        self.fields['section6_text'].widgetFactory = WYSIWYGWidget
        self.fields['section7_text'].widgetFactory = WYSIWYGWidget


    def updateWidgets(self):
        super(DoormatSettings, self).updateWidgets()



class DoormatSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DoormatSettings
