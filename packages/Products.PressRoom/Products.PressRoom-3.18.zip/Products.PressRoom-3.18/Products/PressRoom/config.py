from Products.CMFCore.permissions import setDefaultRoles

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *

PROJECTNAME = "PressRoom"
SKINS_DIR = 'skins'
PERMISSIONS = {
    'PressRoom': 'PressRoom: Add portal press rooms',
    'PressClip': 'PressRoom: Add press clips',
    'PressContact': 'PressRoom: Add press contacts',
    'PressRelease': 'PressRoom: Add press releases',
    }

for permission in PERMISSIONS.values():
    setDefaultRoles(permission, ('Manager', 'Contributor', 'Site Administrator'))

product_globals=globals()