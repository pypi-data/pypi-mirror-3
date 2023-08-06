__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"

import os, sys
import unittest

from zope.component import getUtility, queryUtility

from gomobile.imageinfo.tests.base import BaseTestCase
from gomobile.imageinfo.interfaces import IImageInfoUtility

from Products.CMFCore.utils import getToolByName

class TestResizeImages(BaseTestCase):
    """
    Test resizing internal and external images.
    """
        
    def test_resize_internal(self):
        """ Check that we can extract width/height from resource based images """
        img  = "++resource++gomobile.mobile/phone_back.png" 
        portal = self.portal
        util = getUtility(IImageInfoUtility)
        data, format = util.getURLResizedImage(img, 32, 32)
        # Assume no exceptions are raisen
        self.assertEqual(format, "png", "Got:" + format)
        
    def test_resize_external(self):
        """ Check that we can extract width/height from resource based images """
        img  = "http://plone.org/logo.jpg" 
        portal = self.portal
        util = getUtility(IImageInfoUtility)
        data, format = util.getURLResizedImage(img, 32, 32)
        assert format == "jpeg"
    
        
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestResizeImages))
    return suite
