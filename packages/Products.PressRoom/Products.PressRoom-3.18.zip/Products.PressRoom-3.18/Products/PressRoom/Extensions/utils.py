"""Install/Uninstall utility functions"""

from Products.CMFCore.utils import getToolByName

def restoreKupuSettings(portal, out):
    """Remove PressRoom types from kupu's linkable & collection types"""
    kupuTool = getToolByName(portal, 'kupu_library_tool', None)
    if kupuTool is None:
        return

    linkable    = list(kupuTool.getPortalTypesForResourceType('linkable'))
    collection  = list(kupuTool.getPortalTypesForResourceType('collection'))
    mediaobject = list(kupuTool.getPortalTypesForResourceType('mediaobject'))

    for t in ("PressRoom","PressRelease","PressClip","PressContact",):
        if t in linkable:
            linkable.remove(t)

    if 'PressRoom' in collection:
        collection.remove('PressRoom')

    kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                   'old_type'      : 'linkable',
                                   'portal_types'  :  linkable},
                                  {'resource_type' : 'mediaobject',
                                   'old_type'      : 'mediaobject',
                                   'portal_types'  :  mediaobject},
                                  {'resource_type' : 'collection',
                                   'old_type'      : 'collection',
                                   'portal_types'  :  collection},))
    print >> out, "Removed reference to PressRoom types from kupu's linkable and collection types"

def restoreTinyMCESettings(portal, out):
    """Remove PressRoom types from TinyMCE's linkable & containsobject types"""
    tinymce = getToolByName(portal, 'portal_tinymce', None)
    if tinymce is None:
        return 
    
    containsobjects = tinymce.containsobjects.splitlines()
    if 'PressRoom' in containsobjects:
        containsobjects.remove('PressRoom')
    tinymce.containsobjects = "\n".join(containsobjects)
    
    linkable = tinymce.linkable.splitlines()
    for t in ("PressRoom","PressRelease","PressClip","PressContact",):
        if t in linkable:
            linkable.remove(t)
    tinymce.linkable = "\n".join(linkable)
    
    print >> out, "Removed reference to PressRoom types from TinyMCE's linkable and containsobject types"

def restorePropertiesSettings(portal, out):
    """Remove PressRoom's contributions to various portal_properties.site_properties props"""
    props_tool = getToolByName(portal, 'portal_properties')
    if hasattr(props_tool, 'site_properties'):
        site_properties = getattr(props_tool, 'site_properties')

        types_not_searched = list(site_properties.getProperty('types_not_searched', []))
        if 'PressContact' in types_not_searched:
            types_not_searched.remove('PressContact')
            site_properties.manage_changeProperties(types_not_searched = types_not_searched)
            print >> out, "Removed PressContact from types_not_searched"

        # default_page_types
        defaultPageTypes = list(site_properties.getProperty('default_page_types', []))
        for t in ("PressRelease","PressClip",):
            if t in defaultPageTypes:
                defaultPageTypes.remove(t)
        site_properties.manage_changeProperties(default_page_types = defaultPageTypes)
        print >> out, "Removed PressRoom types from default page types"

        # use_folder_tabs (i couldn't find any installation code for this, but it 
        # still seems to be getting added to this property)
        use_folder_tabs = list(site_properties.getProperty('use_folder_tabs', []))
        if 'PressRoom' in use_folder_tabs:
            use_folder_tabs.remove('PressRoom')
            site_properties.manage_changeProperties(use_folder_tabs = use_folder_tabs)
            print >> out, "Removed PressRoom from use_folder_tabs"

        # typesLinkToFolderContentsInFC (same thing: i couldn't find any installation
        # code for this, but it still seems to be getting added to this property)
        typesLinkToFolderContentsInFC = list(site_properties.getProperty('typesLinkToFolderContentsInFC', []))
        if 'PressRoom' in typesLinkToFolderContentsInFC:
            typesLinkToFolderContentsInFC.remove('PressRoom')
            site_properties.manage_changeProperties(typesLinkToFolderContentsInFC = typesLinkToFolderContentsInFC)
            print >> out, "Removed PressRoom from typesLinkToFolderContentsInFC"

def restoreViewMethods(portal, out):
    """Remove 'folder_listing_pressroom' view from topic's list of view methods"""
    types_tool = getToolByName(portal, 'portal_types')
    topicFTI = types_tool.getTypeInfo('Topic')
    if topicFTI:
        view_methods = list(topicFTI.view_methods)
        if 'folder_listing_pressroom' in view_methods:
            view_methods.remove('folder_listing_pressroom')
            topicFTI.view_methods = tuple(view_methods)
            print >> out, "Removed 'folder_listing_pressroom' view from topic's list of view methods"
