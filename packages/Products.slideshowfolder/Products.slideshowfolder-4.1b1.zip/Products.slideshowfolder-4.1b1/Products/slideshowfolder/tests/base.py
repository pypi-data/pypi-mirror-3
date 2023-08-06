"""
Base class for integration tests, based on ZopeTestCase and PloneTestCase.
   
Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase

# Let Zope know about the products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct('CMFonFive')
ZopeTestCase.installProduct('slideshowfolder')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite


# Set up a Plone site.
setupPloneSite(products=['slideshowfolder'])

class SlideshowFolderTestCase(PloneTestCase):
    """Base class for integration tests for the 'slideshowfolder' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """
    def afterSetUp( self ):
        pass
        
class SlideshowFolderFunctionalTestCase(FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """
    def afterSetUp( self ):
        pass


