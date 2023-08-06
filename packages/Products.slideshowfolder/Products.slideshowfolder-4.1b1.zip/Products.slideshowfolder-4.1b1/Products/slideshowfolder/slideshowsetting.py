"""
module: slideshowfolder
created by: Johnpaul Burbank <jpburbank@tegus.ca>
Date: July 8, 2007
"""

# Zope
from zope.interface import implements
from persistent.dict import PersistentDict
try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations

#from AccessControl import ClassSecurityInfo
#from Products.CMFCore import permissions

#Project
from interfaces import ISlideShowSettings
from config import PROJ


class SlideShowSettings(object):
    """Implementation of ISlideShowSettings. Provides properties from the schema of the interface."""
    implements(ISlideShowSettings)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self._metadata = annotations.get(PROJ, None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations[PROJ] = self._metadata

    def __getattr__(self, name):
        return self._metadata.get(name, ISlideShowSettings[name].default)

    def __setattr__(self, name, value):
        if name[0] == '_' or name == 'context':
            self.__dict__[name] = value
        else:
            self._metadata[name] = value
