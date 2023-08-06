"""
module: slideshowfolder
created by: Johnpaul Burbank <jpburbank@tegus.ca>
Date: July 8, 2007
"""

#Zope / Z3
from zope.interface import Interface
from zope import schema

from Products.slideshowfolder import SlideshowFolderMessageFactory as _


class ISlideShowFolder(Interface):
    """ Marker interface for a folder that holds content that implements ISlideshowImage"""


class ISlideshowImage(Interface):
    """ Interface for content items that can act as slideshow images.

        Such content should have an Archetypes ImageField called 'image'.
    """


class ISlideShowSettings(Interface):
    """Slide show setting fields"""

    # size = schema.Choice(
    #     title=_(u'label_image_size', default=u'Image size'),
    #     description=_(u'help_image_size', default=u'Select the image size to display.'),
    #     required=True,
    #     vocabulary=u'Products.slideshowfolder.vocabularies.image_size_vocabulary',
    #     default='large',
    #     )

    showWidth = schema.Int(
        title=_(u'label_slideshow_width',
                default=u'Slideshow Width'),
        description=_(u'help_slideshow_width',
                      default=u'Width of the slideshow in pixels.  Images '
                              u'will be shrunk to fit within the dimensions '
                              u'of the slideshow.'),
        default=600,
        )

    showHeight = schema.Int(
        title=_(u'label_slideshow_height',
                default=u'Slideshow Height'),
        description=_(u'help_slideshow_height',
                      default=u'Height of the slideshow in pixels.  Images '
                              u'will be shrunk to fit within the dimensions '
                              u'of the slideshow.'),
        default=450,
        )

    # slideTransition = schema.TextLine(
    #     title=u'Transition type',
    #     description=u'Transition between slides',
    #     default=TRANSITIONS[0],
    #     )

    slideDuration = schema.Int(
        title=_(u'label_slide_duration', default=u'Slide Duration'),
        description=_(u'help_slide_duration', default=u'Time in seconds between slide transitions'),
        default=5,
        )

    # panAmount = schema.TextLine(
    #     title=u'Pan Amount',
    #     description=u'Amount to pan images.  Only used for pan and combo transitions.  Enter a value from 0 to 100 or rand for a random amount. You must set width smaller than the width of the smallest image for panning to work.',
    #     default=u'rand',
    #     )
    #
    # zoomAmount = schema.TextLine(
    #     title=u'Zoom Amount',
    #     description=u'Amount to zoom images.  Only used for zoom and combo transitions.  Enter a value from 0 to 100 or rand for a random amount. Note that zoom effects can look a bit weird on Windows/IE.',
    #     default=u'rand',
    #     )

    transitionTime = schema.Float(
        title=_(u'label_trasition_time', default=u'Transition Time'),
        description=_(u'help_transition_time', default=u'Time in seconds for a slide transition to take place.'),
        default=0.5,
        )

    thumbnails = schema.Bool(
        title=_(u'label_thumbnail_mode', default=u'Thumbnail Mode'),
        description=_(u'help_thumbnail_mode', default=u'Include navigation thumbnails below the image.'),
        default=True,
        )

    fast = schema.Bool(
        title=_(u'label_fast_mode', default=u'Fast Mode'),
        description=_(u'help_fast_mode', default=u'Skips the slide transition when a user clicks on a thumbnail.'),
        )

    captions = schema.Bool(
        title=_(u'label_show_captions', default=u'Show Captions'),
        description=_(u'help_show_captions', default=u'Include captions below the image.'),
        default=True,
        )

    arrows = schema.Bool(
        title=_(u'label_show_controller', default=u'Show Controller'),
        description=_(u'help_show_controller', default=u'Include play/pause/forward/back controller in the slideshow.'),
        default=True,
        )

    # paused = schema.Bool(
    #     title=_(u'label_click_to_start', default=u'Click to start slideshow'),
    #     description=_(u'help_click_to_start', default=u'If selected, user must click slideshow to start.'),
    #     )

    random = schema.Bool(
        title=_(u'label_random_order', default=u'Random order'),
        description=_(u'help_random_order', default=u'Shows slides in a random order.'),
        )

    loop = schema.Bool(
        title=_(u'label_loop_slideshow', default=u'Loop Slideshow'),
        description=_(u'help_loop_slideshow', default=u'Repeats the slideshow once it has finished.'),
        default=True,
        )

    linked = schema.Bool(
        title=_(u'label_link_images', default=u'Link images'),
        description=_(u'help_link_images', default=u'Link images to full-sized version'),
        )


class ISlideShowView(Interface):
    """Browser view for the slide show folder"""

    def setWorkflowFilter(wf_filter='published'):
        """ Sets the review_state which will be used to filter the slideshow.  Defaults
            to 'published'.  May be set to None to disable filtering.
        """

    def getSlideshowImages():
        """Returns a list of images for the current slideshowfolder in a dict.
           Keys: 'name', 'caption'.
        """

    def getSlideshowSettings():
        """ Returns a dict of settings for the current slideshowfolder.
        """

    def getSlideshowSize():
        """ Returns a dict containing the name of the slideshow's image size,
            the width, and the height.
        """

    def getControllerTranslations():
        """ Returns a list of dicts, each containing the 'id' and 'msg' for a
            slideshow controller button.
        """


class IFolderSlideShowView(Interface):
    """Provides view methods in regards to the transition from folder to slideshow folder"""

    def isSlideshow():
        """Returns true if we're implementing the ISlideShowFolder interface.

        (Note: we're using implementation of that interface as a proxy for a few other
        behaviors that aren't technically w/in the scope of the interface, such
        as having the view selected and the config tab added.)"""

    def makeSlideshow():
        """Make a folderish object a slideshowfolder"""

    def unmakeSlideshow():
        """Remove all traces of slideshow-ness from a folder"""
