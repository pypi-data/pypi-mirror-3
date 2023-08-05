#
# The Press Room container.
#
# A Press Room is pre-populated with the following Large Plone Folders:
#
# /press-contacts
# /press-clips
# /press-releases
#
# The main goals of these folders are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#

import transaction

# CMF/ZOPE
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

# AT
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

# ATCT
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

# Plone
from Products.CMFPlone.i18nl10n import utranslate

# PR
from Products.PressRoom import HAS_PLONE40
from Products.PressRoom.config import *
from Products.PressRoom.interfaces.content import IPressRoom


ATPressRoomSchema = ATFolderSchema.copy()
ATPressRoomSchema += Schema((
    BooleanField('show_releases',
        required=0,
        default=True,
        widget = BooleanWidget(
            label = "Display Releases?",
            label_msgid = "label_show_releases",
            description = "If this is checked, your published releases will appear.",
            description_msgid = "help_show_release",
            i18n_domain = "pressroom",),
        ),
    IntegerField('num_releases',
        required=0,
        default=4,
        widget = IntegerWidget(
            label = "Number of press releases",
            label_msgid = "label_num_releases",
            description = "What is the maximum number of press releases that should appear in the press room default view?",
            description_msgid = "help_num_releases",
            i18n_domain = "pressroom",),
        ),
    BooleanField('show_clips',
        required=0,
        default=True,
        widget = BooleanWidget(
            label = "Display clips?",
            label_msgid = "label_show_clips",
            description = "If this is checked, your published clips will appear.",
            description_msgid = "help_show_clips",
            i18n_domain = "pressroom",),
        ),
    IntegerField('num_clips',
        required=0,
        default=4,
        widget = IntegerWidget(
            label = "Number of press clips",
            label_msgid = "label_num_clips",
            description = "What is the maximum number of press clips that should appear in the press room default view?",
            description_msgid = "help_num_clips",
            i18n_domain = "pressroom",),
        ),
    BooleanField('show_contacts',
        required=0,
        default=True,
        widget = BooleanWidget(
            label = "Display contacts?",
            label_msgid = "label_show_contacts",
            description = "If this is checked, your published contacts will appear.",
            description_msgid = "help_show_contacts",
            i18n_domain = "pressroom",),
        ),
    TextField('text',
        required=0,
        primary=1,
        searchable=1,
        default_output_type='text/x-html-safe',
        allowable_content_types=('text/restructured',
                                'text/plain',
                                'text/html'),
        widget = RichWidget(
            description = "",
            description_msgid = "help_body_text",
            label = "Body Text",
            label_msgid = "label_body_text",
            rows = 25,
            i18n_domain = "pressroom",)
        ),
    ))

finalizeATCTSchema(ATPressRoomSchema, folderish=True, moveDiscussion=False)

class PressRoom(ATFolder):
    """A folder where all the press related materials in the site live"""
    schema = ATPressRoomSchema
    _at_rename_after_creation = True
    typeDescription= """A folder where all the press related materials in the site live"""
    typeDescMsgId  = 'description_edit_press_room'
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    implements(IPressRoom)


    # Enable marshalling via WebDAV/FTP/ExternalEditor.
    __dav_marshall__ = True

    def initializeArchetype(self, **kwargs):
        """Pre-populate the press room folder with its basic folders.
        """
        ATFolder.initializeArchetype(self,**kwargs)
        
        # create sub-folders
        self._createSubFolders()

    def _createSubFolders(self, use_large_folders=True):
        """We're splitting this out and giving the optional arg just
        to facilitate testing."""

        folder_type = "Folder"
        if HAS_PLONE40:
            use_large_folders = False
        elif use_large_folders:
            folder_type = "Large Plone Folder"
            # enable the addition of LPFs momentarily
            large_folders_addable = True
            portal_types = getToolByName(self, "portal_types")
            lpf = getattr(portal_types, folder_type)
            if not lpf.global_allow:
                large_folders_addable = False
                lpf.manage_changeProperties(global_allow = True)

        if 'press-releases' not in self.objectIds():
            self.invokeFactory(folder_type, 'press-releases')
            obj = self['press-releases']
            obj.setConstrainTypesMode(1)
            obj.setImmediatelyAddableTypes(["PressRelease",])
            obj.setLocallyAllowedTypes(["Topic","PressRelease",])

            obj.setTitle(utranslate('pressroom', 'Press Releases', context=self))
            obj.setDescription(utranslate('pressroom', 'These are our press releases', context=self))
            obj.reindexObject()

            # create Smart Folder to be this folder's default page
            obj.invokeFactory('Topic','all-press-releases')
            obj.setDefaultPage('all-press-releases')

            smart_obj = obj['all-press-releases']
            smart_obj.setTitle(utranslate('pressroom', u'Press Releases', context=self))
            smart_obj.setDescription(utranslate('pressroom', u'These are our press releases', context=self))
            smart_obj.setLayout('folder_listing_pressroom')
            smart_obj.reindexObject()

            state_crit = smart_obj.addCriterion('review_state',
                                                'ATSimpleStringCriterion')
            state_crit.setValue('published')

            type_crit = smart_obj.addCriterion('Type',
                                               'ATPortalTypeCriterion')
            type_crit.setValue('Press Release')

            path_crit = smart_obj.addCriterion('path',
                                               'ATPathCriterion')
            path_crit.setValue(self.UID())
            path_crit.setRecurse(True)

            smart_obj.addCriterion('getReleaseDate','ATSortCriterion')
            smart_obj.getSortCriterion().setReversed(True)

            # Update Smart Folder settings  
            smart_folder_tool = getToolByName(self, 'portal_atct') 
            if 'getReleaseDate' not in smart_folder_tool.getIndexes(enabledOnly=True):     
                smart_folder_tool.addIndex("getReleaseDate", "Release Date", "The date of the press release", enabled=True) 
            elif 'getReleaseDate' not in smart_folder_tool.getIndexes():
                # index exists, but is disabled 
                smart_folder_tool.updateIndex('getReleaseDate', enabled=True)
            if 'getReleaseDate' not in smart_folder_tool.getAllMetadata(enabledOnly=True):
                smart_folder_tool.addMetadata("getReleaseDate", "Release Date", "The date of the press release", enabled=True)
            elif 'getReleaseDate' not in smart_folder_tool.getAllMetadata():     
                # metadata exist, but are disabled     
                smart_folder_tool.updateMetadata('getReleaseDate', enabled=True) 

        if 'press-clips' not in self.objectIds():
            self.invokeFactory(folder_type, 'press-clips')
            obj = self['press-clips']
            obj.setConstrainTypesMode(1)
            obj.setImmediatelyAddableTypes(["PressClip",])
            obj.setLocallyAllowedTypes(["Topic","PressClip",])

            obj.setTitle(utranslate('pressroom', u'Press Clips', context=self))
            obj.setDescription(utranslate('pressroom', u'See us in the news!', context=self))
            obj.reindexObject()

            # create Smart Folder to be this folder's default page
            obj.invokeFactory('Topic','all-press-clips')
            obj.setDefaultPage('all-press-clips')

            smart_obj = obj['all-press-clips']
            smart_obj.setTitle(utranslate('pressroom', u'Press Clips', context=self))
            smart_obj.setDescription(utranslate('pressroom', u'See us in the news!', context=self))
            smart_obj.setLayout('folder_listing_pressroom')
            smart_obj.reindexObject()

            state_crit = smart_obj.addCriterion('review_state',
                                                'ATSimpleStringCriterion')
            state_crit.setValue('published')
            type_crit = smart_obj.addCriterion('Type',
                                               'ATPortalTypeCriterion')
            type_crit.setValue('Press Clip')
            smart_obj.addCriterion('getStorydate','ATSortCriterion')
            path_crit = smart_obj.addCriterion('path',
                                               'ATPathCriterion')
            path_crit.setValue(self.UID())
            path_crit.setRecurse(True)
            smart_obj.getSortCriterion().setReversed(True)

            # Update Smart Folder settings  
            if 'getStorydate' not in smart_folder_tool.getIndexes(enabledOnly=True):     
                smart_folder_tool.addIndex("getStorydate", "Story Date", "The date of the press clip", enabled=True) 
            elif 'getStorydate' not in smart_folder_tool.getIndexes():
                # index exists, but is disabled 
                smart_folder_tool.updateIndex('getStorydate', enabled=True)
            if 'getStorydate' not in smart_folder_tool.getAllMetadata(enabledOnly=True):
                smart_folder_tool.addMetadata("getStorydate", "Release Date", "The date of the press clip", enabled=True)
            elif 'getStorydate' not in smart_folder_tool.getAllMetadata(): 
                # metadata exist, but are disabled     
                smart_folder_tool.updateMetadata('getStorydate', enabled=True)     



        if 'press-contacts' not in self.objectIds():
            self.invokeFactory("Folder", 'press-contacts')
            obj = self['press-contacts']
            obj.setConstrainTypesMode(1)
            obj.setImmediatelyAddableTypes(["PressContact",])
            obj.setLocallyAllowedTypes(["Topic","PressContact",])
            obj.setTitle(utranslate('pressroom', u'Press Contacts', context=self))
            obj.setDescription(utranslate('pressroom', u'Contact these people for more information', context=self))
            obj.reindexObject()

            # create Smart Folder to be this folder's default page
            obj.invokeFactory('Topic','press-contacts')
            obj.setDefaultPage('press-contacts')

            smart_obj = obj['press-contacts']
            smart_obj.setTitle(utranslate('pressroom', u'Press Contacts', context=self))
            smart_obj.setDescription(utranslate('pressroom', u'Contact these people for more information', context=self))
            smart_obj.setLayout('folder_listing_pressroom')
            smart_obj.reindexObject()

            # set the criteria published, type, public, and ordering
            state_crit = smart_obj.addCriterion('review_state',
                                                'ATSimpleStringCriterion')
            state_crit.setValue('published')
            type_crit = smart_obj.addCriterion('Type',
                                               'ATPortalTypeCriterion')
            type_crit.setValue('Press Contact')
            path_crit = smart_obj.addCriterion('path',
                                               'ATPathCriterion')
            path_crit.setValue(self.UID())
            path_crit.setRecurse(True)
            smart_obj.addCriterion('getObjPositionInParent','ATSortCriterion')

        if use_large_folders and not large_folders_addable:
            lpf.manage_changeProperties(global_allow = False)

        transaction.savepoint()

    def manage_afterAdd(self, item, container):
        ATFolder.manage_afterAdd(self, item, container)

    security = ClassSecurityInfo()

registerType(PressRoom, PROJECTNAME)
