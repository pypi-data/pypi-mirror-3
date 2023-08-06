from base import SlideshowFolderTestCase
from Products.slideshowfolder.browser import FolderSlideShowView

class TestSlideshowFolderProductUninstall(SlideshowFolderTestCase):
    def afterSetUp(self):
        # tools
        self.folder.invokeFactory('Folder', id="test1", title="Test Slideshow",)
        self.test1 = getattr(self.folder, 'test1')
        view = FolderSlideShowView(self.test1, self.app.REQUEST)
        view.makeSlideshow()
                
    def testFoldersAreNoLongerSlideshows(self):
        """Uninstall should unslideshow-ify all existing slideshows"""
        view = FolderSlideShowView(self.test1, self.app.REQUEST)
        self.failUnless(view.isSlideshow())
        
        # uninstall our product
        qi = self.portal.portal_quickinstaller
        if qi.isProductInstalled('slideshowfolder'):
            qi.uninstallProducts(products=['slideshowfolder',])

        # that should have made test1 not a Slideshow Folder
        self.failUnless(not view.isSlideshow())

    def testObjectActionsGoneAfterUninstall(self):
        """Uninstall shouldn't leave any traces in portal_actions"""
        # uninstall our product
        qi = self.portal.portal_quickinstaller
        if qi.isProductInstalled('slideshowfolder'):
            qi.uninstallProducts(products=['slideshowfolder',])

        # no actions are left in portal_actions
        action_ids = [a.id for a in self.portal.portal_actions.listActions()]
        self.failIf('makeSlideshow' in action_ids)
        self.failIf('unmakeSlideshow' in action_ids)
        self.failIf('slideshow_settings' in action_ids)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSlideshowFolderProductUninstall))
    return suite
