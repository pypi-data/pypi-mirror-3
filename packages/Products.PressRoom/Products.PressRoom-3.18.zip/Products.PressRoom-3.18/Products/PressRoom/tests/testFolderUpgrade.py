import transaction

from Products.CMFCore.utils import getToolByName

from Products.PressRoom import HAS_PLONE40
from Products.PressRoom.tests import PressRoomTestCase

class TestFolderUpgrade(PressRoomTestCase.PressRoomTestCase):
    """Ensure that upgraded old Press Room subfolders get upgraded properly
    to Large Plone Folders"""

    # we're doing most of the heavy testing in one giant method, bc of all the content
    # creation that it requires
    def testUpgrade(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('PressRoom', id="pressroom", title="Press Room",)
        wf = getToolByName(self.portal, "portal_workflow")
        pressroom = getattr(self.folder, 'pressroom')
        type_mapping = {'press-releases': "PressRelease",
                        'press-clips': "PressClip",
                        }
        home_mapping = {'press-releases':'all-press-releases',
                        'press-clips':'all-press-clips',
                        }

        # nuke the subfolders; recreate them as mere Folders.
        pressroom.manage_delObjects(type_mapping.keys())
        pressroom._createSubFolders(use_large_folders=False)

        # create some sample content and publish the folder
        for sub, typ in type_mapping.items():
            f = getattr(pressroom, sub)
            id = "sample-%s" % (sub)      # so yeah, the id is plural.  who cares?
            f.invokeFactory(typ, id)
            wf.doActionFor(f, 'publish')

        transaction.savepoint(optimistic=True) # (avoid CopyErrors)
        # upgrade!
        pressroom.restrictedTraverse("@@upgrade-folders")()

        # can we finally start testing?
        for sub in type_mapping.keys():
            f = getattr(pressroom, sub)

            # in Plone 3, are they Large Plone Folders?
            if HAS_PLONE40:
                self.assertEqual(f.portal_type, 'Folder')
            else:
                self.assertEqual(f.portal_type, "Large Plone Folder")

            # content moved?
            self.failUnless("sample-%s" % (sub) in f.objectIds())

            # default page?
            self.assertEqual(f.default_page, home_mapping[sub])

            # WF state?
            self.assertEqual(wf.getInfoFor(f, 'review_state'), 'published')

            # title/descr?

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFolderUpgrade))
    return suite
