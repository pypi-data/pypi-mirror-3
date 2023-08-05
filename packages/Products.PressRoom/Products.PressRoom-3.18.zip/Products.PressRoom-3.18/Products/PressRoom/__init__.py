from Products.CMFCore import utils, DirectoryView
from Products.Archetypes.public import *
from Products.Archetypes import listTypes

from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.CMFPlone.interfaces import IPloneSiteRoot

# Get configuration data, permissions
from Products.PressRoom.config import *

# Register skin directories so they can be added to portal_skins
 
DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/pressroom_content', product_globals)
DirectoryView.registerDirectory('skins/pressroom_content_2.5', product_globals)
DirectoryView.registerDirectory('skins/pressroom_scripts', product_globals)
DirectoryView.registerDirectory('skins/pressroom_styles', product_globals)

# message factory code stolen from CMFPlone 2.5
# Import "PressRoomMessageFactory as _" to create message ids in the pressroom domain
# Zope 3.1-style messagefactory module
# BBB: Zope 2.8 / Zope X3.0
try:
    from zope.i18nmessageid import MessageFactory
except ImportError:
    from messagefactory_ import PressRoomMessageFactory
else:
    PressRoomMessageFactory = MessageFactory('pressroom')

def initialize(context):

    # Import the type, which results in registerType() being called
    from content import PressRoom, PressRelease, PressClip, PressContact
    
    # initialize the content, including types and add permissions
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    for content_type, constructor, fti in zip(content_types, constructors, ftis):
        utils.ContentInit(
            PROJECTNAME + ' Content',
            content_types      = (content_type,),
            permission         = PERMISSIONS[content_type.portal_type],
            extra_constructors = (constructor,),
            fti                = (fti,),
            ).initialize(context)

    # Register the extension profile
    profile_registry.registerProfile('default',
                                     'PressRoom',
                                     'pressroom',
                                     'profiles/default',
                                     'PressRoom',
                                     EXTENSION,
                                     IPloneSiteRoot)

# Parts of the installation process depend on the version of Plone.
# This release supports Plone 2.5.3 and Plone 3.
try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    HAS_PLONE30 = False
else:
    HAS_PLONE30 = True

try:
    # The folder Products.CMFPlone.migrations does not exist in Plone 4
    # anymore, see plone.app.upgrade
    from plone.app.upgrade import v40
except ImportError:
    HAS_PLONE40 = False
else:
    HAS_PLONE30 = True
    HAS_PLONE40 = True
