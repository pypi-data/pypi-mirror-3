from zope.interface import implements

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *

from Products.ATContentTypes.content.newsitem import ATNewsItem, ATNewsItemSchema, \
                                                     finalizeATCTSchema

from Products.PressRoom.config import *
from Products.PressRoom import PressRoomMessageFactory as _
from Products.PressRoom.interfaces.content import IPressClip

schema = ATNewsItemSchema.copy()

# text field not required for clips
schema['text'].required = 0

schema += Schema((
    StringField('reporter',
                required=0,
                searchable=0,
                primary=False,
                languageIndependent=0,
                #index="FieldIndex:brains",
                widget=StringWidget(
                        label='Reporter\'s Name',
                        label_msgid = "label_reporter_name",
                        description='Provide the name of the reporter',
                        description_msgid = "help_reporter_name",
                        i18n_domain = "pressroom",),
                ),

    StringField('publication',
                required=0,
                searchable=1,
                primary=0,
                languageIndependent=1,
                Multivalues=1,
                #index="FieldIndex:brains",
                widget=StringWidget(
                        label='Name of Publication',
                        label_msgid = "label_publication_name",
                        description='Provide the name of the publication (i.e. name of newspaper, magazine, book, website, etc.).',
                        description_msgid = "help_publication_name",
                        i18n_domain = "pressroom",),
                ),
    StringField('permalink',
                #index="FieldIndex:brains",
                widget=StringWidget(
                        label='URL of Press Clip',
                        label_msgid = "label_pressclip_url",
                        description='Provide the URL to the Press Clip',
                        description_msgid = "help_pressclip_url",
                        i18n_domain = "pressroom",),
                ),
    DateTimeField('storydate',
                #index="DateIndex:brains",
                required=1,
                widget=CalendarWidget(
                        label='Story Date',
                        label_msgid = "label_pressclip_storydate",
                        description='The date the clip was originally published',
                        description_msgid = "help_pressclip_storydate",
                        i18n_domain = "pressroom",),
                ),              
    ))

finalizeATCTSchema(schema)

class PressClip(ATNewsItem):
    """For organization's press clips."""
    # meta_type = portal_type = 'PressClip'
    # archetype_name = 'Press Clip'    
    # #immediate_view = 'pressclip_view'
    #default_view   = 'pressclip_view'
    #content_icon   = 'pressclip_icon.gif'
    typeDescription = """For organization's press clips."""
    typeDescMsgId  = """press_clip_description_edit"""
    schema         = schema
    exclude_from_nav = True
    
    _at_rename_after_creation = True
    
    # Get the standard actions (tabs)
    actions = ATNewsItem.actions

    implements(IPressClip)

    # enable FTP/WebDAV and friends
    PUT = ATNewsItem.PUT


registerType(PressClip, PROJECTNAME)
