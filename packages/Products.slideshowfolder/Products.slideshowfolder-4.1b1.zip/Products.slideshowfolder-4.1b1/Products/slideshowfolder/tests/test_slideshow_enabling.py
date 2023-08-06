from base import SlideshowFolderTestCase
from Products.slideshowfolder.browser import FolderSlideShowView
from Products.slideshowfolder.config import PROJ
from Products.slideshowfolder.slideshowsetting import SlideShowSettings
from Products.slideshowfolder import HAS_PLONE3UP

try:
    from zope.annotation.interfaces import IAnnotations #For Zope 2.10.4
except ImportError:
    from zope.app.annotation.interfaces import IAnnotations #For Zope 2.9


class TestSlideshowEnabling(SlideshowFolderTestCase):
    """Test the enabling and disabling of slideshows within folders"""

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Folder', id="test1", title="Test Slideshow",)
        self.test1 = getattr(self.folder, 'test1')

    def testEnablingSlideshow(self):
        """Test that we can enable the slideshow functionality on a folder
        that doesn't yet have it"""
        view = FolderSlideShowView(self.test1, self.app.REQUEST)

        # not yet enabled
        self.failUnless(not view.isSlideshow())

        # we have an object action to enable it
        action_id = 'makeSlideshow'
        actions = self.portal.portal_actions.listFilteredActionsFor(self.test1)
        action_ids = [a['id'] for a in actions['object_buttons']]
        self.failUnless(action_id in action_ids,
                        "Uh oh! %s not found in %s" % (action_id, action_ids))

        # enable it
        view.makeSlideshow()

        # prove that it's enabled
        self.failUnless(view.isSlideshow())

        # just testing plone 3 for now
        if HAS_PLONE3UP:
            # prove that we have the slideshow settings tab, too
            actions = self.portal.portal_actions.listFilteredActionsFor(self.test1)
            action_ids = [a['id'] for a in actions['object']]
            action_id  = 'slideshow_settings'
            self.failUnless(action_id in action_ids,
                            "Uh oh! %s not found in %s" % (action_id, action_ids))


    def testEnabledSlideshowIsEnabled(self):
        """Test that an enabled slideshow delivers what it promises."""
        view = FolderSlideShowView(self.test1, self.app.REQUEST)
        view.makeSlideshow()

        # our 'layout' (ie default view template) should be folder_slideshow
        layout = getattr(self.test1, "layout", "")
        self.failUnless(layout=='folder_slideshow')

        # we should have an object action to unmake the slideshow
        action_id = 'unmakeSlideshow'
        actions = self.portal.portal_actions.listFilteredActionsFor(self.test1)
        action_ids = [a['id'] for a in actions['object_buttons']]
        self.failUnless(action_id in action_ids,
                        "Uh oh! %s not found in %s" % (action_id, action_ids))

        # we should have a tab for slideshow configuration
        action_id = 'slideshow_settings'
        actions = self.portal.portal_actions.listFilteredActionsFor(self.test1)
        if actions.has_key('object_tabs'):
            # plone 2.5
            action_ids = [a['id'] for a in actions['object_tabs']]
        else:
            # plone 3
            action_ids = [a['id'] for a in actions['object']]
        self.failUnless(action_id in action_ids,
                        "Uh oh! %s not found in %s" % (action_id, action_ids))

        # and just for thoroughness (this is already tested elsewhere)
        # prove that we're implementing the ISlideShowFolder interface (which is all this method does)
        self.failUnless(view.isSlideshow())

    def testDisablingSlideshow(self):
        """We want to make sure that we're thoroughly removing the cruft"""
        view = FolderSlideShowView(self.test1, self.app.REQUEST)
        view.makeSlideshow()
        # set some data so that we're sure that the annotations are created
        metadata_setter = SlideShowSettings(self.test1)
        metadata_setter.slideDuration=2
        view.unmakeSlideshow()

        # the most basic: we're no longer implementing the ISlideShowFolder interface
        self.failUnless(not view.isSlideshow())

        # our 'layout' (ie default view template) shouldn't be folder_slideshow
        layout = getattr(self.test1, "layout", "")
        self.failUnless(layout != 'folder_slideshow')

        # we should again have an object action to make the slideshow
        action_id = 'makeSlideshow'
        actions = self.portal.portal_actions.listFilteredActionsFor(self.test1)
        action_ids = [a['id'] for a in actions['object_buttons']]
        self.failUnless(action_id in action_ids,
                        "Uh oh! %s not found in %s" % (action_id, action_ids))

        # just testing plone 3 for now
        if HAS_PLONE3UP:
            # we should no longer have the slideshow settings tab
            actions = self.portal.portal_actions.listFilteredActionsFor(self.test1)
            action_ids = [a['id'] for a in actions['object']]
            action_id  = 'slideshow_settings'
            self.failIf(action_id in action_ids,
                        "%s still listed in available actions: %s" % (action_id, action_ids))


        # check that we're no longer storing annotation data here
        annotations = IAnnotations(self.test1)
        self.failUnless(annotations.get(PROJ, None) is None,
                        "Annotations not deleted: %s" % annotations.get(PROJ))

    def testLayoutProperty(self):
        """ Make sure property calls work after unmaking a slideshowfolder """
        self.test1._setProperty('layout', 'foobar', 'string')

        view = FolderSlideShowView(self.test1, self.app.REQUEST)
        view.makeSlideshow()
        self.failUnlessEqual(self.test1.layout, 'folder_slideshow')
        view.unmakeSlideshow()
        self.failUnlessEqual(self.test1.propertyItems(),
                             [('title', u'Test Slideshow')])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSlideshowEnabling))
    return suite
