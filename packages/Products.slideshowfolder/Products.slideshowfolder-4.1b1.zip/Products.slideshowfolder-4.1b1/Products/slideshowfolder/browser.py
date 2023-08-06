"""
module: slideshowfolder
created by: Johnpaul Burbank <jpburbank@tegus.ca>
Date: July 8, 2007
"""

import re

#Zope / Z3
from zope.interface import implements, providedBy, alsoProvides

try:
    from zope.interface import noLongerProvides
    has_zope_3_3 = True
except ImportError:
    # BBB - to remove after support for 2.5 is no longer included
    has_zope_3_3 = False
    from zope.interface import directlyProvides, directlyProvidedBy

try:
    from plone.memoize.view import memoize
    has_memoize = True
except ImportError:
    has_memoize = False

from Products.Five.browser import BrowserView
from Acquisition import aq_inner

from zope.formlib import form
from plone.app.form import base as ploneformbase

from Products.slideshowfolder import SlideshowFolderMessageFactory as _

#Plone
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.topic import IATTopic
from Products.ATContentTypes.interface.image import IATImage
#from Products.ATContentTypes.content.image import ATImageSchema

#Project
from Products.slideshowfolder.interfaces import ISlideShowSettings, \
    ISlideShowView, IFolderSlideShowView, ISlideShowFolder, ISlideshowImage
from Products.slideshowfolder.slideshowsetting import SlideShowSettings
from Products.slideshowfolder.config import PROJ
from Products.slideshowfolder import HAS_PLONE3UP

try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAttributeAnnotatable
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAttributeAnnotatable
    from zope.app.annotation.interfaces import IAnnotations

if HAS_PLONE3UP:
    # Images don't have a workflow by default.
    WF_FILTER = None
    IMAGE_FILTER = dict(
        object_provides = (
            IATImage.__identifier__,
            ISlideshowImage.__identifier__,
            ),
        )
else:
    WF_FILTER = 'published'
    IMAGE_FILTER = dict(
        meta_type = 'ATImage',
        )

image_re = re.compile(r'^.*\.jpe?g$|\.gif$|\.png$', re.IGNORECASE)


class SlideShowFolderView(BrowserView):
    implements(ISlideShowView)

    __catalog_args = IMAGE_FILTER
    wf_filter = WF_FILTER

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.settings = SlideShowSettings(self.context)

    def setWorkflowFilter(self, wf_filter = WF_FILTER):
        self.wf_filter = wf_filter

    def _uncached_getSlideshowElements(self):
        """Convenience method to do the actual catalog calls.  Returns a list of brains or None"""

        if IATTopic.providedBy(self.context):
            # If we're dealing with something that looks like a Smart Folder/Collection,
            # use its criteria for getting images.  If not, we'll use our own.
            results = self.context.queryCatalog(**self.__catalog_args)
        else:
            # Not Topical, we're assuming it's otherwise folderish
            cat = getToolByName(self.context, 'portal_catalog')
            args = dict(**self.__catalog_args)
            path = '/'.join(self.context.getPhysicalPath())
            args['path'] = {'query': path, 'depth': 1}
            args['sort_on'] = 'getObjPositionInParent'
            if self.wf_filter is not None:
                args['review_state'] = self.wf_filter
            results = cat(**args)

        return results

    def _getImageCaption(self, item):
        caption = item.Description
        if not caption:
            caption = item.Title
            if image_re.match(caption):
                caption = ''

        """Return a javascript-safe version of an Image's description"""
        caption = caption.decode('UTF-8')
        # escape single quotes
        caption = caption.replace("'", "\\'")
        # remove newlines
        caption = caption.replace('\n', ' ')
        caption = caption.replace('\r', ' ')
        return caption

    def getSlideshowImages(self):
        brains = self._getSlideshowElements()
        pics = []
        for item in brains:
            pic_info = dict(
                name = "%s/image_large" % (item.getURL()),
                caption = self._getImageCaption(item)
                )
            pics.append(pic_info)
        return pics

    def getSlideshowSettings(self):
        """Returns a list of settings for the current slideshowfolder in a dict."""

        #Building the javascript string
        options = {}
        if self.settings.transitionTime:
            options['duration'] = int(self.settings.transitionTime*1000)
        if self.settings.slideDuration:
            options['delay'] = int(self.settings.slideDuration*1000)
        options['thumbnails'] = self.settings.thumbnails and 'true' or 'false'
        options['captions'] = self.settings.captions and 'true' or 'false'
        options['loop'] = self.settings.loop and 'true' or 'false'
        options['linked'] = self.settings.linked and 'true' or 'false'
        # options['loader'] = loader and 'true' or 'false'
        size = self.getSlideshowSize()
        options['replace'] = "[/image_%s/, 'image_tile']" % size['name']
        options['width'] = size['width']
        options['height'] = size['height']
        # options['paused'] = self.settings.paused and 'true' or 'false'
        options['paused'] = 'false'
        options['random'] = self.settings.random and 'true' or 'false'
        options['controller'] = self.settings.arrows and 'true' or 'false'
        options['fast'] = self.settings.fast and 'true' or 'false'
        return options

    def getSlideshowSize(self):
        return dict(
            name = u'large',
            width = self.settings.showWidth,
            height = self.settings.showHeight,
            )

    def getControllerTranslations(self):
        # we'll use this once the js library actually gets it right
        #play_pause = self.settings.paused and 'play' or 'pause'
        play_pause = 'pause'
        translations = {
            'first': _(u'title_controller_first', default=u'First [Shift + Left arrow]'),
            'prev': _(u'title_controller_prev', default=u'Previous [Left arrow]'),
            play_pause: _(u'title_controller_pause', default=u'Play / Pause [P]'),
            'next': _(u'title_controller_next', default=u'Next [Right arrow]'),
            'last': _(u'title_controller_last', default=u'Last [Shift + Right arrow]'),
            }
        return [{'id': id, 'msg': msg} for id, msg in translations.items()]

    # cache the _getSlideshowElements and getAvailableImageSizes methods since they are
    # called twice per request (but only if memoize is available)
    if has_memoize and HAS_PLONE3UP:

        @memoize
        def _getSlideshowElements(self):
            return self._uncached_getSlideshowElements()
    else:
        _getSlideshowElements = _uncached_getSlideshowElements


class FolderSlideShowView(BrowserView):
    """Provides view methods in regards to the transition from folder to slideshow folder"""
    implements(IFolderSlideShowView)
    iprovides = (IAttributeAnnotatable, ISlideShowFolder)

    def isSlideshow(self):
        """Returns true if we're implementing the ISlideShowFolder interface.

        (Note: we're using implementation of that interface as a proxy for a few other
        behaviors that aren't technically w/in the scope of the interface, such
        as having the view selected and the config tab added.)"""
        return ISlideShowFolder.providedBy(self.context)

    def makeSlideshow(self):
        """Make a folderish object a slideshowfolder"""
        # two steps: provide interfaces, manually set "layout"
        for inter in self.iprovides:
            if not inter.providedBy(self.context):
                alsoProvides(self.context, inter)

        folder = aq_inner(self.context)
        if folder.hasProperty('layout'):
            folder._updateProperty('layout', 'folder_slideshow')
        else:
            folder._setProperty('layout', 'folder_slideshow', 'string')

        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.addPortalMessage(_(u'message_slideshow_created',
            default=u"This folder is now designated a slideshow."))

        if hasattr(self.request, 'RESPONSE'):
            self.request.RESPONSE.redirect(self.context.absolute_url())

    def unmakeSlideshow(self):
        """Remove all traces of slideshow-ness from a folder"""
        folder = aq_inner(self.context)
        # 1) stop providing the interface
        # AFAICT, there's no direct opposite of alsoProvides
        # I got the following technique from a IRC chat transcript:
        #           http://zope3.pov.lt/irclogs/%23zope3-dev.2007-03-19.log.html
        # (search for "IUCSubSite")
        if ISlideShowFolder in providedBy(folder) and has_zope_3_3:
            noLongerProvides(folder, ISlideShowFolder)
        elif ISlideShowFolder in providedBy(folder) and not has_zope_3_3:
            # BBB - TODO: Remove after support for Plone 2.5.x stops
            directlyProvides(folder, directlyProvidedBy(folder)-ISlideShowFolder)

        # 2) delete the "layout" attribute
        # This way, we'll fallback gracefully to whatever the current default view for folders is
        if folder.hasProperty('layout'):
            folder._delProperty('layout')

        # 3) we should delete the metadata saved in the annotation, too
        annotations = IAnnotations(self.context)
        if annotations.has_key(PROJ):
            del annotations[PROJ]

        if hasattr(self.request, 'RESPONSE'):
            plone_utils = getToolByName(self.context, 'plone_utils')
            plone_utils.addPortalMessage(_(u'message_slideshow_removed',
                default=u"Completely removed slideshow capabilities."))
            self.request.RESPONSE.redirect(self.context.absolute_url())


class SlideShowSettingsForm(ploneformbase.EditForm):

    form_fields = form.FormFields(ISlideShowSettings)

    label = _(u'heading_slideshow_settings_form',
        default=u"Slideshow folder settings")

    description = _(u'description_slideshow_settings_form',
        default=u"Configure the parameters for this slideshow folder.")

    form_name = _(u'title_slideshow_settings_form',
        default=u"Slideshow folder settings")
