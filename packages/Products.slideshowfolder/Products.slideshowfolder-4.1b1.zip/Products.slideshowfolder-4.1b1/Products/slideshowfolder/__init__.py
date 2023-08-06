"""
module: slideshowfolder
created by: Johnpaul Burbank <jpburbank@tegus.ca>
Date: July 8, 2007
"""

# CMFCore
from Products.CMFCore.DirectoryView import registerDirectory
# CMFPlone
from Products.CMFPlone.interfaces import IPloneSiteRoot
# Generic Setup
from Products.GenericSetup import EXTENSION, profile_registry

# message factory for i18n
from zope.i18nmessageid import MessageFactory
SlideshowFolderMessageFactory = MessageFactory('slideshowfolder')

# Allow access from restricted python to some modules.
from AccessControl import allow_module, allow_class
allow_module('Products.slideshowfolder.interfaces')
from Products.slideshowfolder.slideshowsetting import SlideShowSettings
allow_class(SlideShowSettings)

from config import GLOBALS
registerDirectory('skins', GLOBALS)

# Parts of the installation process depend on the version of Plone.
# This release supports Plone 2.5.x and Plone 3 up.
try:
    from plone.app.upgrade import v40
except ImportError:
    try:
        from Products.CMFPlone.migrations import v3_0
    except ImportError:
        HAS_PLONE3UP = False
    else:
        HAS_PLONE3UP = True
else:
    HAS_PLONE3UP = True

# Make zope aware of our permission
from Products.CMFCore.permissions import setDefaultRoles
if HAS_PLONE3UP:
    setDefaultRoles('Slideshowfolder: Manage slideshow settings', ('Manager', 'Editor', 'Owner'))
else:
    # Plone 2.5 doesn't have an editor role
    setDefaultRoles('Slideshowfolder: Manage slideshow settings', ('Manager', 'Owner'))

def initialize(context):
    profile_registry.registerProfile(
        'default',
        'slideshowfolder',
        'Installs slideshowfolders skins directory',
        'profiles/default',
        'slideshowfolder',
        EXTENSION,
        for_=IPloneSiteRoot,
    )

    if HAS_PLONE3UP:
        profile_registry.registerProfile(
        'plone3',
        'slideshowfolder plone3 actions',
        'Installs slideshowfolders version-specific actions',
        'profiles/plone3',
        'slideshowfolder',
        EXTENSION,
        for_=IPloneSiteRoot,
        )

