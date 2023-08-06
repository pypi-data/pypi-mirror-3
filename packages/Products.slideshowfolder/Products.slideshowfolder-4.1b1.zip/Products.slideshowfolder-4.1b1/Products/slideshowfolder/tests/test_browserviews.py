# -*- coding: utf-8 -*-

import os
from zope.interface import alsoProvides
from Products.CMFCore.utils import getToolByName

from base import SlideshowFolderTestCase
from Products.slideshowfolder import HAS_PLONE3UP
from Products.slideshowfolder.browser import FolderSlideShowView
from Products.slideshowfolder.browser import SlideShowFolderView
from Products.slideshowfolder.interfaces import ISlideshowImage

from Globals import package_home
PACKAGE_HOME = package_home(globals())

# borrowed from ATCT's test_atimage
def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = os.path.join(PACKAGE_HOME, 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data

TEST_IMAGE = loadImage('test.jpg')

class TestBrowserViews(SlideshowFolderTestCase):
    def afterSetUp(self):
        """Load a real image for use in tests"""
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Folder', id="test_folder", title="Test Slideshow",)
        self.test_folder = getattr(self.folder, 'test_folder')
        self.test_folder.invokeFactory('Image', 'test.jpg')
        self.test_image = getattr(self.test_folder, 'test.jpg')
        self.test_image.setImage(TEST_IMAGE, mimetype='image/jpg', filename='test.jpg')
        self.test_image.setDescription(u'Qué linda esta flor')
        self.test_image.setTitle('Flower Power')
        self.test_image.reindexObject()
        if not HAS_PLONE3UP:
            workflow = getToolByName(self.portal, 'portal_workflow')
            workflow.doActionFor(self.test_image, 'publish')


    def testFolderAsSlideShow(self):
        view = FolderSlideShowView(self.test_folder, self.app.REQUEST)
        view.makeSlideshow()
        slideshow_view = SlideShowFolderView(self.test_folder, self.app.REQUEST)

        images = slideshow_view.getSlideshowImages()
        self.assertEqual(len(images), 1)
        self.failUnless(images[0]['name'].endswith('image_large'))
        # we're implicitly testing the Unicode-ness of the description-as-caption
        self.assertEqual(images[0]['caption'], u'Qué linda esta flor')

        settings = slideshow_view.getSlideshowSettings()
        for setting in ('duration', 'delay', 'thumbnails', 'captions', 'loop', 'linked', 'replace',
            'width', 'height', 'paused', 'random', 'controller', 'fast'):
            self.failUnless(settings.has_key(setting))

    def testTopicAsSlideShow(self):
        self.folder.invokeFactory('Topic', 'sf')
        topic = getattr(self.folder, 'sf')
        title_crit = topic.addCriterion('Title', 'ATSimpleStringCriterion')
        title_crit.setValue('Flower')

        view = FolderSlideShowView(topic, self.app.REQUEST)
        view.makeSlideshow()
        slideshow_view = SlideShowFolderView(topic, self.app.REQUEST)

        # shouldn't return non-images even if they are valid given the criteria
        self.folder.invokeFactory('Document', 'mydoc')
        self.folder.mydoc.setTitle('Flower')
        self.folder.mydoc.reindexObject()
        images = slideshow_view.getSlideshowImages()
        self.assertEqual(len(images), 1)

        images = slideshow_view.getSlideshowImages()
        self.assertEqual(len(images), 1)
        self.failUnless(images[0]['name'].endswith('image_large'))
        # we're implicitly testing the Unicode-ness of the description-as-caption
        self.assertEqual(images[0]['caption'], u'Qué linda esta flor')

        settings = slideshow_view.getSlideshowSettings()
        for setting in ('duration', 'delay', 'thumbnails', 'captions', 'loop', 'linked', 'replace',
            'width', 'height', 'paused', 'random', 'controller', 'fast'):
            self.failUnless(settings.has_key(setting))

        # should return anything providing ISlideshowImage that matches the criteria
        alsoProvides(self.folder.mydoc, ISlideshowImage)
        self.folder.mydoc.reindexObject()
        images = slideshow_view._uncached_getSlideshowElements()
        self.assertEqual(len(images), 2, '(Known failure on Plone 2.5)')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserViews))
    return suite
