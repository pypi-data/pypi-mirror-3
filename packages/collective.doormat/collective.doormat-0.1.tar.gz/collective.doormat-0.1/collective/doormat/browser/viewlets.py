from zope.component import getUtility
from plone.app.layout.viewlets import common as base

from plone.registry.interfaces import IRegistry
from collective.doormat.interfaces import IDoormatSettingsSchema



class DoormatViewlet(base.ViewletBase):
    """ Inserts the doormat into the portal footer """

    sections = []
    header = None
    footer = None

    def update(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDoormatSettingsSchema)
        self.header = settings.doormat_header
        self.footer = settings.doormat_footer
        self.sections = []
        sections = settings.enabled_sections
        for section in sections:
            name = getattr(settings, section + '_title')
            url =  getattr(settings, section + '_link')
            text =  getattr(settings, section + '_text')
            self.sections.append({'url': url, 'name': name, 'text': text})
