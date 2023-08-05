from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.PressRoom import HAS_PLONE30
from Products.PressRoom.config import *
from Products.PressRoom.Extensions.utils import restoreKupuSettings, \
                                                restoreTinyMCESettings, \
                                                restorePropertiesSettings, \
                                                restoreViewMethods
def install(portal):
    """Install press room content types, skin layer, stylesheet, 
    set up global properties, enable the portal factory
    """

    out = StringIO()

    print >> out, "Installing Press Room's Generic Setup profile"
    setup_tool = getToolByName(portal, 'portal_setup')
    if HAS_PLONE30:
        setup_tool.runAllImportStepsFromProfile('profile-PressRoom:default')
    else:
        original_context = setup_tool.getImportContextID()
        setup_tool.setImportContext('profile-PressRoom:default')
        setup_tool.runAllImportSteps()
        setup_tool.setImportContext(original_context)

    return out.getvalue()

def uninstall(portal, reinstall=False):
    """Remove PressRoom cruft"""
    out = StringIO()

    print >> out, "Uninstalling Press Room"
    # 1: Fix editor settings
    restoreKupuSettings(portal, out)
    restoreTinyMCESettings(portal, out)
    # 2: Remove PressRoom's contributions to various portal_properties.site_properties props
    restorePropertiesSettings(portal, out)
    # 3: Remove 'folder_listing_pressroom' view from topic's list of view methods
    restoreViewMethods(portal, out)
    return out.getvalue()
