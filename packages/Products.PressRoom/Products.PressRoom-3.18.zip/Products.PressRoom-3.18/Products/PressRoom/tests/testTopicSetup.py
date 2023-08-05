#
# Test Press Room Topic (aka Smart Folder or Collection) setup
#

from Products.PressRoom.tests import PressRoomTestCase

class TestTopicSetup(PressRoomTestCase.PressRoomTestCase):
    """Ensure content types can be created and edited"""

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('PressRoom', id="pressroom", title="Press Room",)
        self.pressroom = getattr(self.folder, 'pressroom')

        self.pressreleases = getattr(self.pressroom, 'press-releases')
        self.allreleases = getattr(self.pressreleases, 'all-press-releases')

        self.pressclips = getattr(self.pressroom, 'press-clips')
        self.allclips = getattr(self.pressclips, 'all-press-clips')

        self.presscontacts = getattr(self.pressroom, 'press-contacts')
        self.contactroster = getattr(self.presscontacts, 'press-contacts')
        
        self.childFolderMapping = {
                                    'press-releases':'all-press-releases',
                                    'press-clips':'all-press-clips',
                                    'press-contacts':'press-contacts',
                                  }

    # test press release smart folders
    def testNumbersOfReleases(self):
        n = 3
        
        # create 3 press releases
        for i in range(n):
            i += 1    
            self.pressreleases.invokeFactory('PressRelease', id="release%s" % i, title="Press Release %s" % i)

        # make sure we've successfully created all 3 of our PressRelease objects
        self.assertEqual(len(self.pressreleases.objectIds("PressRelease")),n)
        
        # see how many topic results we've got, should be 0 because none have been published
        self.assertEqual(len(self.allreleases.queryCatalog()),0)
        
        # now publish all releases and test length of topic
        workflow = self.portal.portal_workflow

        for i in range(n):
            i += 1    
            self.releaseObj = getattr(self.pressreleases, "release%s" % i)
            workflow.doActionFor(self.releaseObj,"publish")

        # see how many topic results we've got, *still* should be 0 because none have a releaseDate value, which is the sort order criteria
        self.assertEqual(len(self.allreleases.queryCatalog()),0)

        # now add a releaseDate value to each
        from DateTime import DateTime

        for i in range(n):
            now = DateTime()
            i += 1    
            self.releaseObj = getattr(self.pressreleases, "release%s" % i)
            self.releaseObj.setReleaseDate(now)
            self.releaseObj.reindexObject()

        # finally, we should have n items        
        self.assertEqual(len(self.allreleases.queryCatalog()),n)

    def testContactRosterCriteria(self):
        # Press Contact topic is in place as default view and has a criterion to show
        # only published Press Contacts sorted by their position in the folder.
        self.assertEqual(self.contactroster._getPortalTypeName(), 'Topic')
        self.assertEqual(self.contactroster.buildQuery()['Type'], ('Press Contact',))
        self.assertEqual(self.contactroster.buildQuery()['review_state'], 'published')
        self.assertEqual(self.contactroster.buildQuery()['path']['query'][0],"/".join(self.pressroom.getPhysicalPath()))
        self.assertEqual(self.contactroster.buildQuery()['path']['depth'],-1)
        self.assertEqual(self.contactroster.getSortCriterion().field,'getObjPositionInParent')

    def testAllPressReleasesCriteria(self):
        # Press Release topic is in place as default view and has a criterion to show
        # only published Press Contacts within the current press room object
        self.assertEqual(self.allreleases._getPortalTypeName(), 'Topic')
        self.assertEqual(self.allreleases.buildQuery()['Type'], ('Press Release',))
        self.assertEqual(self.allreleases.buildQuery()['review_state'], 'published')
        self.assertEqual(self.allreleases.buildQuery()['path']['query'][0],"/".join(self.pressroom.getPhysicalPath()))
        self.assertEqual(self.allreleases.buildQuery()['path']['depth'],-1)
        self.assertEqual(self.allreleases.getSortCriterion().field,'getReleaseDate')
        self.assertEqual(self.allreleases.getSortCriterion().getReversed(),True)

    def testAllPressClipCriteria(self):
        # Press Clip topic is in place as default view and has a criterion to show
        # only Press Clips with published press clips within the appropriate path location
        self.assertEqual(self.allclips._getPortalTypeName(), 'Topic')
        self.assertEqual(self.allclips.buildQuery()['Type'], ('Press Clip',))
        self.assertEqual(self.allclips.buildQuery()['review_state'], 'published')
        self.assertEqual(self.allclips.buildQuery()['path']['query'][0],"/".join(self.pressroom.getPhysicalPath()))
        self.assertEqual(self.allclips.buildQuery()['path']['depth'],-1)
        self.assertEqual(self.allclips.getSortCriterion().field,'getStorydate')
        self.assertEqual(self.allclips.getSortCriterion().getReversed(),True)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTopicSetup))
    return suite

