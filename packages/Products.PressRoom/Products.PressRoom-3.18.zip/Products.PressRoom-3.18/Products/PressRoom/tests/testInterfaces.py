from zope.interface.verify import verifyObject, verifyClass

from Products.PressRoom.interfaces import browserviews
from Products.PressRoom.interfaces import content
from Products.PressRoom.browser.pressroom import PressRoom as PressRoomView
from Products.PressRoom.content.PressRoom import PressRoom
from Products.PressRoom.content.PressClip import PressClip
from Products.PressRoom.content.PressRelease import PressRelease
from Products.PressRoom.content.PressContact import PressContact

from Products.PressRoom.tests import PressRoomTestCase

class TestInterfaces(PressRoomTestCase.PressRoomTestCase):
    """Ensure our classes provide the specified interfaces"""

    def afterSetUp(self):
        self.setRoles(['Manager'])
    
    def testBrowserViews(self):
        self.failUnless(browserviews.IPressRoom.implementedBy(PressRoomView))
        self.failUnless(verifyClass(browserviews.IPressRoom, PressRoomView))

    def testPressRoom(self):
        self.failUnless(content.IPressRoom.implementedBy(PressRoom))
        self.failUnless(verifyClass(content.IPressRoom, PressRoom))

        id = 'pr'
        self.folder.invokeFactory("PressRoom", id)
        obj = getattr(self.folder, id)
        self.failUnless(verifyObject(content.IPressRoom, obj))

    def testPressContact(self):
        self.failUnless(content.IPressContact.implementedBy(PressContact))
        self.failUnless(verifyClass(content.IPressContact, PressContact))

        id = 'test'
        self.folder.invokeFactory("PressContact", id)
        obj = getattr(self.folder, id)
        self.failUnless(verifyObject(content.IPressContact, obj))

    def testPressClip(self):
        self.failUnless(content.IPressClip.implementedBy(PressClip))
        self.failUnless(verifyClass(content.IPressClip, PressClip))

        id = 'test'
        self.folder.invokeFactory("PressClip", id)
        obj = getattr(self.folder, id)
        self.failUnless(verifyObject(content.IPressClip, obj))

    def testPressRelease(self):
        self.failUnless(content.IPressRelease.implementedBy(PressRelease))
        self.failUnless(verifyClass(content.IPressRelease, PressRelease))

        id = 'test'
        self.folder.invokeFactory("PressRelease", id)
        obj = getattr(self.folder, id)
        self.failUnless(verifyObject(content.IPressRelease, obj))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInterfaces))
    return suite

