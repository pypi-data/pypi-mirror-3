from zope.interface import implements
from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.log import log_deprecated

from Products.PressRoom.interfaces import IPressRoom
from Products.PressRoom import HAS_PLONE30

class PressRoom(BrowserView):
    """Browser view for the Press Room CT"""

    implements(IPressRoom)
    
    # BBB This method is deprecated and will be removed in PressRoom 4.0.
    def getContacts(self):
        """Return  a list of Press Contacts for this Press Room only if they should be shown
        """
        log_deprecated('getContacts is deprecated and will be removed'
                       'in PressRoom 4.0. Please update your pressroom_view template'
                       'to query the appropriate collection directly.')
             
        if self.context.getShow_contacts():
            source = self.context.restrictedTraverse('press-contacts/press-contacts', None)
            if source:
                return source.queryCatalog()
        return ()

    def canAddPressContacts(self):
        """Returns True if the current user has permission to add Press Contacts"""
        membership_tool = getToolByName(self.context, 'portal_membership')
        return membership_tool.checkPermission('PressRoom: Add press contacts', self.context)
        
    # BBB This method is deprecated and will be removed in PressRoom 4.0.
    def getReleases(self):
        """Return  a list of Press Releases for this Press Room only if they should be shown
        """
        log_deprecated('getReleases is deprecated and will be removed'
                       'in PressRoom 4.0. Please update your pressroom_view template'
                       'to query the appropriate collection directly.')
             
        if self.context.getShow_releases():
            source = self.context.restrictedTraverse('press-releases/all-press-releases', None)
            if source:
                return source.queryCatalog()
        return ()

    def canAddPressReleases(self):
        """Returns True if the current user has permission to add Press Releases"""
        membership_tool = getToolByName(self.context, 'portal_membership')
        return membership_tool.checkPermission('PressRoom: Add press releases', self.context)
        
    # BBB This method is deprecated and will be removed in PressRoom 4.0.
    def getClips(self):
        """Return  a list of Press Clips for this Press Room only if they should be shown
        """
        log_deprecated('getClips is deprecated and will be removed'
                       ' in PressRoom 4.0. Please update your pressroom_view template'
                       ' to query the appropriate collection directly.')
             
        if self.context.getShow_clips():
            source = self.context.restrictedTraverse('press-clips/all-press-clips', None)
            if source:
                return source.queryCatalog()
        return ()

    def canAddPressClips(self):
        """Returns True if the current user has permission to add Press Clips"""
        membership_tool = getToolByName(self.context, 'portal_membership')
        return membership_tool.checkPermission('PressRoom: Add press clips', self.context)

    def showTwoStatePrivateWarning(self):
        """Returns True if we're in Plone 3.0, the press room's supporting folders are private,
           and the current user is someone who can do something about it."""
        context = aq_inner(self.context)
        if not HAS_PLONE30:
            return False
        else:
            membership_tool = getToolByName(self.context, 'portal_membership')
            if not membership_tool.checkPermission('Review portal content', self.context):
                return False
            else:
                workflow_tool   = getToolByName(self.context, 'portal_workflow')
                for fn in ('press-releases', 'press-clips', 'press-contacts'):
                    folder = getattr(context, fn, None)
                    if folder is None:
                        return False
                    if workflow_tool.getInfoFor(folder, 'review_state') != 'private':
                        return False

        return True

    def publishPressRoomInfrastructure(self):
        """Publish the 3 content folders (clips, releases, contacts) and the Collections
        that are their home folders.  If the Press Room is unpublished, publish it too"""
        # this is usually relevant to only Plone 3.0, but is there any reason to exclude 2.5 use
        # at this point?

        # I decided to not make showTwoStatePrivateWarning a dependency at this level to allow
        # people who published one of the folders manually before realizing the issue.
        # That way, they can call this to fix the reset

        workflow_tool = getToolByName(self.context, 'portal_workflow')
        context = aq_inner(self.context)
        infrastructure = {'press-releases':'all-press-releases',
                          'press-clips':'all-press-clips',
                          'press-contacts':'press-contacts',
                          }

        for fn in infrastructure.keys():
            folder = getattr(context, fn, None)
            if folder:
                if workflow_tool.getInfoFor(folder, 'review_state') == 'private':
                    workflow_tool.doActionFor(folder, 'publish')
                sf = getattr(folder, infrastructure[fn], None)
                if sf and workflow_tool.getInfoFor(sf, 'review_state') == 'private':
                    workflow_tool.doActionFor(sf, 'publish')
                    
        # if the Press Room itself is unpublished, take care of it too -- note
        # we need to be clear that this is part of the effect
        if workflow_tool.getInfoFor(context, 'review_state') == 'private':
            workflow_tool.doActionFor(context, 'publish')
            IStatusMessage(self.request).addStatusMessage(_("Press Room published"),
                                                          type="info")

        IStatusMessage(self.request).addStatusMessage(_("Press Room infrastructure published"),
                                              type="info")

        self.request.response.redirect(context.absolute_url())
