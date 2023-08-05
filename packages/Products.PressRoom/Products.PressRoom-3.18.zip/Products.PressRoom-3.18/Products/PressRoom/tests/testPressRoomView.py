#
# Test Press Room content type initialization
#

from Products.CMFCore.utils import getToolByName
from Products.PressRoom.tests import PressRoomTestCase
from Products.PressRoom import HAS_PLONE30
from Products.PressRoom.browser.pressroom import PressRoom as PR_view # crowded namespace, no?

class TestPressRoomView(PressRoomTestCase.PressRoomTestCase):
    """Ensure content types can be created and edited"""

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('PressRoom', id="pressroom", title="Press Room",)
        self.pressroom = getattr(self.folder, 'pressroom')
        
    def testShowTwoStatePrivateWarning(self):
        """Returns True if we're in Plone 3.0, the press room's supporting folders are private,
           and the current user is someone who can do something about it."""
        view = PR_view(self.pressroom, self.app.REQUEST)
        
        # should always return False if we're not in Plone 3
        if not HAS_PLONE30:
            self.failUnless(view.showTwoStatePrivateWarning() is False)
        else:
            # by default, it should return True for a straight out-of-the-box site
            showW = view.showTwoStatePrivateWarning()
            self.failUnless(showW is True,
                            "showTwoStatePrivateWarning returned %s" % showW)
            
            # publish the folders: now it should return False
            workflow = getToolByName(self.portal, 'portal_workflow')
            for fn in ('press-releases', 'press-clips', 'press-contacts'):
                f = getattr(self.pressroom, fn)
                workflow.doActionFor(f, 'publish')
            view = PR_view(self.pressroom, self.app.REQUEST)
            showW = view.showTwoStatePrivateWarning()
            self.failUnless(showW is False,
                            "showTwoStatePrivateWarning returned %s" % showW)
            
            # change WFs to simulate community wf (plone_wf for topics and pressrooms
            # and plone_folder_wf for folders) and create a new pressroom
            self.simulateCommunityWF()
            self.folder.invokeFactory('PressRoom', id="pressroom2", title="Press Room 2",)
            view = PR_view(self.folder.pressroom2, self.app.REQUEST)
            self.failUnless(view.showTwoStatePrivateWarning() is False)
        
    def testPublishPressRoomInfrastructure(self):
        """Publish the 3 content folders (clips, releases, contacts) and the Collections
        that are their home folders"""
        if HAS_PLONE30:
            # out of the box, we should show the warning in 3.0
            view = PR_view(self.pressroom, self.app.REQUEST)
            self.failUnless(view.showTwoStatePrivateWarning() is True)
            # publish the folders
            view.publishPressRoomInfrastructure()
            # now it should be False
            self.failUnless(view.showTwoStatePrivateWarning() is False)

    def simulateCommunityWF(self):
        """Make minimal changes to simulate the 2.5 style WF defaults"""
        from plone.app.workflow.remap import remap_workflow
        # remap_workflow(self.portal, type_ids=('PressRoom', 'Topic'), 
        #                chain=('plone_workflow',))
        remap_workflow(self.portal, type_ids=('Folder',), 
                       chain=('folder_workflow',))
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.setDefaultChain('plone_workflow')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPressRoomView))
    return suite
