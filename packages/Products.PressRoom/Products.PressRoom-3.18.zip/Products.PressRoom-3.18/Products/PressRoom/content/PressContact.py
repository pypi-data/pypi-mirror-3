from zope.interface import implements

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *

from Products.ATContentTypes.content.base import ATCTContent

from Products.PressRoom.config import *
from Products.PressRoom import PressRoomMessageFactory as _
from Products.PressRoom.interfaces.content import IPressContact

# set Base Schema as the schema
schema = BaseSchema.copy()

# remove the distraction of short name, since it's not relevant for a press contact
schema['id'].widget.visible = {'edit': 'invisible', 'view': 'invisible'}  
schema['title'].widget.label = 'Name'

schema += Schema((
    StringField('jobtitle',
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=1,
                widget=StringWidget(
                        label='Job Title',
                        label_msgid = "label_job_title",
                        description='Enter the official job title of the press contact (i.e. Chief Technology Officer, Executive Director, Director of Human Resources)',
                        description_msgid = "help_job_title",
                        i18n_domain = "pressroom",),
                ),
    StringField('email',
                validators = ('isEmail',),
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=0,
                widget=StringWidget(
                        label='Email Address',
                        label_msgid = "label_email_address",
                        description='Provide the email address for this press contact',
                        description_msgid = "help_email_address",
                        i18n_domain = "pressroom",),
                ),
    StringField('city',
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=1,
                widget=StringWidget(
                        label='City',
                        label_msgid = "label_city",
                        description='Provide the city for this press contact',
                        description_msgid = "help_city",
                        i18n_domain = "pressroom",),
                ),
    StringField('stateOrProvince',
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=1,
                widget=StringWidget(
                        label='State or Province',
                        label_msgid = "label_state_or_province",
                        description='Provide the state or province for this press contact',
                        description_msgid = "help_state_or_province",
                        i18n_domain = "pressroom",),

                ),
    StringField('organization',
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=1,
                widget=StringWidget(
                        label='Organization',
                        label_msgid = "label_organization",
                        description="""With which organization is this press contact affiliated.""",
                        description_msgid = "help_organization",
                        i18n_domain = "pressroom",),
                ),
    StringField('phone',
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=1,
                widget=StringWidget(
                        label='Telephone Number',
                        label_msgid = "label_telephone_number",
                        description="""Provide a telephone number for this press contact.""",
                        description_msgid = "help_telephone_number",
                        i18n_domain = "pressroom",),
                ),
    StringField('cellphone',
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=1,
                widget=StringWidget(
                        label='Cellphone Number',
                        label_msgid = "label_cellphone_number",
                        description="""""",
                        description_msgid = "help_cellphone_number",
                        i18n_domain = "pressroom",),
                ),    
    TextField('text',
        required=0,
        primary=1,
        searchable=1,
        default_output_type='text/x-html-safe',
        allowable_content_types=('text/html',),
        widget = RichWidget(
            description = "A description of the press contact (such as their focus areas, job responsibilities, expertise, etc.)",
            # we use the old msgid for compatibility with existing translations
            description_msgid = "help_description",
            label = "Description",
            label_msgid = "label_description",
            rows = 5,
            i18n_domain = "pressroom",)
          ),
    
    ))

class PressContact(ATCTContent):
    """Contact information for your press contacts. Can be referenced in press releases."""
    typeDescription = """Contact information for your press contacts"""
    typeDescMsgId  = """press_contact_description_edit"""
    schema         = schema
    exclude_from_nav = True
    
    _at_rename_after_creation = True
    implements(IPressContact)

    def getRawText(self, raw=False, **kwargs):
        # BBB for old description field
        raw = self.getField('text').getRaw(self, raw=raw, **kwargs)
        if raw:
            return raw
        return '<p class="documentDescription">%s</p>' % self.Description()
    
    def getText(self, mimetype=None, raw=False, **kwargs):
        # BBB for old description field
        text = self.getField('text').get(self, mimetype=mimetype, raw=raw, **kwargs)
        if text:
            return text
        return '<p class="documentDescription">%s</p>' % self.Description()

registerType(PressContact, PROJECTNAME)
