About 
=====

Slideshow Folder provides a simple, elegant animated slideshow for
Plone.

Slideshow Folder integrates the `Slideshow 2` javascript class into
Plone. Slideshow 2 a powerful, feature-rich, easy-to-customize slideshow
library -- big thanks to Aeron Glemann all of the hard work he's poured
into it!

.. _`Slideshow 2`: http://www.electricprism.com/aeron/slideshow

Slideshow Folder offers the following features:

 * Animated slideshows with configurable transitions

 * Navigation thumbnails

 * Image captions

 * Intelligent preloading of images to save bandwidth

 * A play/pause/forward/reverse slideshow controller

 * Looping and random-order slideshows

 * Optional support for "lightbox" style image pop-ups

 * Look and feel completely customizable via CSS

Design Rationale
====================

Slideshow Folder uses Zope 3 development techniques to enable normal Plone 
Folders, Collections and Images with configurable slideshow views.

We wanted to develop a slideshow product for Plone that would avoid creating
custom content types for the images and slideshow folders in order to allow 
easy installation, re-use of existing images in the site and to avoid 
"stranding" content in future upgrades or when you remove the product.


Dependencies 
====================

Slideshow Folder is easiest to install and use under Plone 3.x, but also 
supports Plone 2.5.2+.  
However, in order to use Slideshow Folder under Plone 2.5, you must be 
comfortable installing software from SVN checkout.

Slideshow Folder requires:

 * Plone 3.0+ strongly recommended (Plone 2.5.2+ works, but requires the 
   following dependences)

 * CMFonFive 1.3.4 (ONLY if using Plone 2.5.x - 
   http://codespeak.net/z3/cmfonfive/)

 * Five 1.4 (ONLY if using Plone 2.5.x - http://codespeak.net/z3/five/)

 * plone.app.form (ONLY if using Plone 2.5.x - check out from
   http://svn.plone.org/svn/plone/plone.app.form/branches/plone-2.5


Installation 
====================

Plone 3.x, buildout-based installer
-----------------------------------

If you are using Plone 3.x via a buildout-based installer, simply add 
"Products.slideshowfolder" to the [eggs] section of your buildout.

 * Beginning with Plone 3.1, Plone's universal installer for Unix uses buildout.
 
 * Plone 3.2 and higher will use buildout for Windows, Mac OSX and Unix 
   universal installers.


Plone 3.0.x, non-buildout installer
-----------------------------------

Slideshow Folder installs in the conventional way.  Unzip the tarball and copy 
the product folder "slideshowfolder" into your Zope Products directory and 
restart your Zope instance.  You can then install it into your Plone site from
the Plone Control Panel or the ZMI's portal_quickinstaller.  Uninstall it the
same way.

Plone 2.5.x, non-buildout installer
-------------------------------------

Download Slideshow Folder and its dependencies, listed above.

Install Slideshow Folder, CMFOnFive and Five in your Zope instance's Products 
folder as normal.

plone.app.form must be checked out from SVN and installed in your Zope's 
instance's lib/python/plone/app/form directory.  It can be a bit tricky to 
unpack the directories correctly.  
Tip: you get a directory called  plone.app.form, but you need to go to your
Zope instance's lib/python folder and do::

  mkdir plone (if it doesn't exist)
  cd plone
  mkdir app (if it doesn't exist)
  cd app
  mkdir form

Then go to your unpacked plone.app.form directory and do::

  mv plone/app/form/*  yourzopeinstance/lib/python/plone/app/form


Plone 2.5.x, buildout-based installation
----------------------------------------

Add "Products.slideshowfolder" to the [eggs] section of your buildout.

Consult buildout documentation for tips on installing CMFOnFive, Five tarballs 
and plone.app.form from SVN.  Warning: this will require some experience using
buildout for more complex installations.


Using Slideshow Folder
======================

Each Folder and Collection in your site will have a new option in its
"action" menu -- "make slideshow". Choosing that will select a slideshow
view for that folder and give you a new "Slideshow Settings"
configuration tab.  As soon as there are published images in the folder,
you'll see the slideshow.  (Collections rely on the criteria that you
put in them to render the images for the slideshow.  Non-images are
ignored.  That means that workflow restrictions are based solely on your
Collection's criteria.)

To change the slideshow's settings, see the new "slideshow settings" tab
on the folder.

Each image's Description will be used for its caption.  If there is no
description, the Title will be used.

Each slideshow will have an "disable slideshow" option in the action
menu.  This will revert it to being a normal Folder (or Smart Folder),
including deleting the slideshow settings.  (It will not delete any
content, though.)

Note: The slideshow will only include published images in the folder.
You can customize this (rather crudely) by customizing
folder_slideshow.pt and calling the setWorkflowFilter method on the
slideshow view.  (Options include "None" or any valid workflow state.)
Consult the interfaces.py for documentation on those methods.
(Alternatively, you can use a Collection and not place any workflow
restrictions on your criteria.)

Note: Only a subset of the options for Aeron Glemann's library
are supported via the 'Slideshow Settings' tab.  See
http://code.google.com/p/slideshow/wiki/Slideshow
for the full list of options.  If customization beyond the options
exposed via the web interface is needed, you can customize
slideshow_settings.js.pt to specify the additional options.

Note: You may use your own custom image content type as long as it
implements the Products.slideshowfolder.interfaces.ISlideshowImage
interface (which requires an Archetypes ImageField named 'image' in
its schema.)  (Plone 3.0+ only.)


Limitations
===========

Slideshow Folder currently has several limitations, most of which flow
from the Slideshow 2 javascript class it is based on.

 * Transitions cannot be set on a per-slide basis, only for all the
   slides in the slideshow.
   
 * In IE, the slideshow does not operate properly when logged in as a
   Manager and accessing the site at http://localhost/.  You can work
   around this by using http://127.0.0.1/ instead.  See
   http://plone.org/products/slideshowfolder/issues/46 for details.


Credits 
=======

Slideshow Folder was written by `Johnpaul Burbank`_, with subsequent
changes by `Jon Baldivieso`_.  Version 4.0 by `David Glick`_.

.. _`Johnpaul Burbank`: http://www.tegus.ca
.. _`Jon Baldivieso`: jonb@onenw.org
.. _`David Glick`: davidglick@onenw.org

Initial concept, project management and a few tweaks by
`ONE/Northwest`_, including Jon Stahl and Andrew Burkhalter.

.. _`ONE/Northwest`: http://www.onenw.org

Special thanks to `Conservation Northwest`_ for partial funding and beta
testing.

.. _`Conservation Northwest`: http://www.conservationnw.org

Slideshow Folder includes and is based on `Slideshow 2`_, by
Aeron Glemann. Slideshow 2 uses the Mootools_ javascript library.

.. _Mootools: http://www.mootools.net


More information
================

Please see http://www.plone.org/products/slideshowfolder for more
information, updates, documentation and bug reports.

ONE/Northwest is a nonprofit organization that provides technology
assistance (including Plone-powered websites!) to environmental NGOs. If
you'd like to support our work, including the release of open-source
software like Slideshow Folder, please see:
http://www.onenw.org/about/supporters/support-our-work

