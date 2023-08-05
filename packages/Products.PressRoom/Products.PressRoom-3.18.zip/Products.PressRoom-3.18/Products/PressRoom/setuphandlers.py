from Products.CMFCore.utils import getToolByName
from Products.PressRoom import HAS_PLONE30
import string
try:
    from Products.kupu.plone.librarytool import KupuError
except ImportError:
    KupuError = None

class PRSetup(object):
    
    def configureKupu(self, portal):
        """Note that while kupu (as of this writing) supported
         Generic Setup profiles, it appeared to demand the entire settings given
         at once -- not incremental changes.  Since we don't want to nuke existing
         settings, we're doing it with code here."""

        # Add FileAttachment and ImageAttachment to kupu's linkable and collection types
        kupuTool = getToolByName(portal, 'kupu_library_tool', None)
        if kupuTool is None:
            return
        
        linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
        collection = list(kupuTool.getPortalTypesForResourceType('collection'))
        mediaobject = list(kupuTool.getPortalTypesForResourceType('mediaobject'))
    
        for t in ("PressRoom","PressRelease","PressClip","PressContact",):
            # validate type using kupu's method; defensive maneuver for elusive bug #44
            try:
                kupuTool._validate_portal_types('linkable', (t,))
                if t not in linkable:
                    linkable.append(t)
            except KupuError:
                # we're swallowing these issues for now
                pass
    
        for t in ('PressRoom',):
            try:
                kupuTool._validate_portal_types('collection', (t,))
                if t not in collection:
                    collection.append(t)
            except KupuError:
                # swallowing for now
                pass
        # kupu_library_tool has an odd interface, basically written purely to
        # work with its configuration page. :-(
        kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                       'old_type'      : 'linkable',
                                       'portal_types'  :  linkable},
                                      {'resource_type' : 'mediaobject',
                                       'old_type'      : 'mediaobject',
                                       'portal_types'  :  mediaobject},
                                      {'resource_type' : 'collection',
                                       'old_type'      : 'collection',
                                       'portal_types'  :  collection},))

    def configureATCT(self, portal):
        """enable two indices to be used by smart folders"""
        smart_folder_tool = getToolByName(portal, 'portal_atct')
        
        # enable "position in parent" index
        index = smart_folder_tool.getIndex("getObjPositionInParent")
        index_def = {'index'        : index.index,
                     'friendlyName' : index.friendlyName,
                     'description'  : index.description,
                     'criteria'     : index.criteria
                    }
        smart_folder_tool.addIndex(enabled=True, **index_def)

        # extend the possible "criteria" for the "Type" criterion 
        typeIndex = smart_folder_tool.getIndex("Type")
        typeIndex_def = {'index'        : typeIndex.index,
                         'friendlyName' : typeIndex.friendlyName,
                         'description'  : typeIndex.description,
                         'criteria'     : typeIndex.criteria + ("ATListCriterion",)
                        }
        smart_folder_tool.addIndex(enabled=True, **typeIndex_def)

        # enable the "Story Date" index with a nicer name
        # what appears to be a bug in 3.0.6 -- unless I list the indexes ahead of time,
        # it can't find the "getStorydate" index.  Not a problem in 2.5.5
        smart_folder_tool.getIndexes()
        index = smart_folder_tool.getIndex("getStorydate")
        index_def = {'index'        : index.index,
                     'friendlyName' : "Story Date",
                     'description'  : """The date a Press Clip ran in its original publication or the date a Press Release was "released".""",
                     'criteria'     : index.criteria
                    }
        smart_folder_tool.addIndex(enabled=True, **index_def)

        return "Enabled the getObjPositionInParent and Story Date indices for use by smart folders.  Updated settings on the Type index field with the portal_atct tool."

    def removeUnneededSkinLayer(self, portal):
        """Our profile installs two different skin layers for content,
        but we only want the one that's appropriate for our version of Plone."""
        skins_tool = getToolByName(portal, "portal_skins")
        if HAS_PLONE30:
            bad_skin = "pressroom_content_2.5"
        else:
            bad_skin = "pressroom_content"
            # Go through the skin configurations and insert the skin

        skins = skins_tool.getSkinSelections()
        for skin in skins:
            path = skins_tool.getSkinPath(skin)
            path = map(string.strip, string.split(path,','))
            if bad_skin in path:
                path.remove(bad_skin) 
                path = string.join(path, ', ')
                # addSkinSelection will replace existing skins as well.
                skins_tool.addSkinSelection(skin, path)

def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profile.
    """
    # don't run as a step for other profiles
    if context.readDataFile('is_pressroom.txt') is None:
        return
    
    site = context.getSite()
    configurator = PRSetup()
    if KupuError is not None:
        configurator.configureKupu(site)
    configurator.configureATCT(site)
    configurator.removeUnneededSkinLayer(site)