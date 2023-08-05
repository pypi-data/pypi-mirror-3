#
# Test Press Room content type initialization
#

from Products.CMFCore.utils import getToolByName

from Products.PressRoom import HAS_PLONE40
from Products.PressRoom.tests import PressRoomTestCase

class TestPressRoomCreation(PressRoomTestCase.PressRoomTestCase):
    """Ensure content types can be created and edited"""

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('PressRoom', id="pressroom", title="Press Room",)
        self.pressroom = getattr(self.folder, 'pressroom')

        self.childFolderMapping = {
                                    'press-releases':'all-press-releases',
                                    'press-clips':'all-press-clips',
                                    'press-contacts':'press-contacts',
                                  }

    def testCreatePressRoom(self):
        self.failUnless('pressroom' in self.folder.objectIds())

    def testEditPressRoom(self):
        self.pressroom.setTitle('Media Center')
        self.pressroom.setDescription('Our Media Center')
        self.pressroom.setNum_releases(5)
        self.pressroom.setNum_clips(5)
        self.pressroom.setShow_contacts(True)
        self.pressroom.setText('<p>Here are our latest <strong>press releases and press clips</strong>:</p>', mimetype='text/html')

        self.assertEqual(self.pressroom.Title(), 'Media Center')
        self.assertEqual(self.pressroom.Description(), 'Our Media Center')
        self.assertEqual(self.pressroom.getNum_releases(), 5)
        self.assertEqual(self.pressroom.getNum_clips(), 5)
        self.assertEqual(self.pressroom.getShow_contacts(), True)
        self.assertEqual(self.pressroom.getText(), '<p>Here are our latest <strong>press releases and press clips</strong>:</p>')
        self.failUnlessRaises(ValueError, self.pressroom.setNum_clips,"Some text")
        self.failUnlessRaises(ValueError, self.pressroom.setNum_releases,"Some text")

    def testPressRoomChildrenCreated(self):
        for f in self.childFolderMapping.keys():
            self.failUnless(f in self.pressroom.objectIds())

    def testPressContactsTypesContrained(self):
        self.presscontacts = getattr(self.pressroom,'press-contacts')
        self.assertEqual(self.presscontacts.getConstrainTypesMode(), 1)
        self.failUnless("PressContact" in self.presscontacts.getLocallyAllowedTypes())
        self.failUnless("Topic" in self.presscontacts.getLocallyAllowedTypes()) 
        self.failUnless("PressContact" in self.presscontacts.getImmediatelyAddableTypes())

    def testPressClipsTypesContrained(self):
        self.presscontacts = getattr(self.pressroom,'press-clips')
        self.assertEqual(self.presscontacts.getConstrainTypesMode(), 1)
        self.failUnless("PressClip" in self.presscontacts.getLocallyAllowedTypes())
        self.failUnless("Topic" in self.presscontacts.getLocallyAllowedTypes()) 
        self.failUnless("PressClip" in self.presscontacts.getImmediatelyAddableTypes())

    def testDefaultPage(self):
        for k,v in self.childFolderMapping.items():
            self.assertEqual(self.pressroom[k].getDefaultPage(), v)

    def testChildrenTopicsCreated(self):
        for k,v in self.childFolderMapping.items():
            self.failUnless(v in self.pressroom[k].objectIds())

    def testLargeFoldersUsed(self):
        for f in self.childFolderMapping.keys():
            if f == 'press-contacts' or HAS_PLONE40:
                # contacts want to be in an *ordered* folder
                self.assertEqual(self.pressroom[f].portal_type, "Folder")
            else:
                # in Plone 3, press releases and clips want to be in BTree folders
                self.assertEqual(self.pressroom[f].portal_type, "Large Plone Folder")

    def testLargeFoldersStillNotAddable(self):
        if HAS_PLONE40:
            return
        
        # we're assuming that the default settings were in place initially: 
        # Large Plone Folders are not implicitly addable
        portal_types = getToolByName(self.portal, 'portal_types')
        lpf = getattr(portal_types, "Large Plone Folder")
        self.failUnless(lpf.global_allow is False)

    def testLargeFoldersStillAddableIfEnabled(self):
        if HAS_PLONE40:
            return
        
        # we're assuming that the default settings were in place initially: 
        # Large Plone Folders are not implicitly addable
        portal_types = getToolByName(self.portal, 'portal_types')
        lpf = getattr(portal_types, "Large Plone Folder")
        lpf.manage_changeProperties(global_allow = True)

        self.folder.invokeFactory('PressRoom', id="pressroom2", title="Press Room 2",)
        self.failIf(lpf.global_allow is False)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPressRoomCreation))
    return suite
