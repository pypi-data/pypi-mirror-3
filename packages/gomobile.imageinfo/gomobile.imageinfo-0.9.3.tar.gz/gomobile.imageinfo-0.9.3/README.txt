.. contents ::

Introduction
------------

``gomobile.imageinfo`` is abstraction layer to access image data in different Zope image objects. 
It takes in any image object or traversable path and returns Python Imaging Library object for it.

The package is a part of mFabrik `Web and Mobile <http://webandmobile.mfabrik.com>`_ solutions package
to build multichannel content management with Python.

Supported different image objects include
    
* Skin layer images, both file system based and ZMI uploads
    
* Archetypes ATImage
    
* Resource folder images (static media)

* Images hosted on another server (http:// download)

This package is mainly used with Go Mobile for Plone project to dynamically resize images for mobile presentation,
regardless what kind of image there was in the source code. It is used to extract image width and height,
calculate proper mobile image size and then resize the image for that size on a second pass.

Usage
-----

See tests for code examples.

TODO
----

* Tests depends on ``gomobile.mobile`` presence

Source code and issue tracking
-----------------------------------

The project is hosted at `Google Code project repository <http://code.google.com/p/plonegomobile>`_.

Commercial support and development
-----------------------------------

This package is licenced under open source GPL 2 license.

`Commercial CMS and mobile development support options <http://webandmobile.mfabrik.com/services>`_
are available from mFabrik's Web and Mobile product site.

Our top class Python developers are ready to help you with 
any software development needs.
  
Author
------

`mFabrik Research Oy <mailto:info@mfabrik.com>`_ - Python and Plone professionals for hire.

* `mFabrik Web & Mobile - multichannel CMS made easy <http://webandmobile.mfabrik.com>`_ 

* `mFabrik web site <http://mfabrik.com>`_ 

* `mFabrik mobile site <http://mfabrik.mobi>`_ 

* `Blog <http://blog.mfabrik.com>`_
