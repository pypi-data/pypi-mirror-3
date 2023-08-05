import transaction
from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.PressRoom import HAS_PLONE40
from Products.PressRoom.interfaces.browserviews import IUpgradeFolders

class UpgradeFolders(BrowserView):
    """This browser view migrates the three main Press Room subfolders to
    unordered folders, to improve performance.  Running this migration is no
    longer needed in Plone 4.
    
    This view is called within the context of a Press Room obj.  It assumes that
    the subfolders retain their original names.  Migration preserves:
    - all content (obviously)
    - 'default page'/'layout' settings
    - addable type constraints
    - folders' Title/descr
    - WF state of folders
    
    Note that calling this browser view might be very resource/time intensive
    if the folders have a lot of content!
    """

    implements(IUpgradeFolders)

    def __call__(self):
        if HAS_PLONE40:
            return ("Migrating to Large Plone Folders is no longer necessary in "
                   "Plone 4.")
        
        # if needed, enable the addition of LPFs momentarily
        large_folders_addable = True
        portal_types = getToolByName(self, "portal_types")
        lpf = getattr(portal_types, "Large Plone Folder")
        if not lpf.global_allow:
            large_folders_addable = False
            lpf.manage_changeProperties(global_allow = True)

        subfolder_ids = ('press-releases','press-clips')
        upgraded = []
        for subfolder_id in subfolder_ids:
            orig = getattr(self.context, subfolder_id, None)
            if orig is not None and orig.portal_type == 'Folder':
                self.context.invokeFactory("Large Plone Folder", 'temp')
                repl = getattr(self.context, 'temp')
                # content
                cb_copy_data = orig.manage_cutObjects(orig.objectIds())
                repl.manage_pasteObjects(cb_copy_data)

                # default page/layout
                old_home = getattr(orig, 'default_page', None)
                if old_home is not None:
                    repl.default_page=old_home
                old_layout = getattr(orig, 'layout', None)
                if old_layout is not None:
                    repl.layout=old_layout

                # addable type constraints
                repl.setConstrainTypesMode(orig.getConstrainTypesMode())
                repl.setImmediatelyAddableTypes(orig.getImmediatelyAddableTypes())
                repl.setLocallyAllowedTypes(orig.getLocallyAllowedTypes())

                # metadata
                repl.setTitle(orig.Title())
                repl.setDescription(orig.Description())

                # WF state.  this one is tricky, bc we have a bunch of different permutations
                # we only handle the most common ones (excluding, particularly, "pending" states)
                portal_workflow = getToolByName(self.context, 'portal_workflow')
                orig_state = portal_workflow.getInfoFor(orig, 'review_state')
                repl_state = portal_workflow.getInfoFor(repl, 'review_state')
                if orig_state != repl_state:
                    if orig_state == 'private':
                        transition = 'hide'
                    elif orig_state == 'published':
                        transition = 'publish'
                    elif orig_state == 'visible':
                        transition = 'show'
                    portal_workflow.doActionFor(repl, transition)

                # delete orig; rename replacement
                transaction.savepoint(optimistic=True) # (avoid CopyErrors)
                self.context.manage_delObjects([subfolder_id,])
                self.context.manage_renameObject('temp', subfolder_id)

                upgraded.append(repl.absolute_url())

        # re-disable LPFs if applicable
        if not large_folders_addable:
            lpf.manage_changeProperties(global_allow = False)

        if upgraded:
            return "Upgraded the following folders: %s" % (', '.join(upgraded))
        else:
            return """No folders were upgraded -- either the subfolders within this Press Room\
                    are already Large Plone Folders or their ids have changed from the default\
                    values"""