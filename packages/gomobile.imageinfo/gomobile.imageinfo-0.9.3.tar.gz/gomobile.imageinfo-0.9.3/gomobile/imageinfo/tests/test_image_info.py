__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import os, sys
import unittest

from zope.component import getUtility, queryUtility

from gomobile.imageinfo.tests.base import BaseTestCase
from gomobile.imageinfo.interfaces import IImageInfoUtility

from Products.CMFCore.utils import getToolByName

class TestImageInfo(BaseTestCase):
    
    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        # Upload an AT field based image
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Image", "test_img")
        
        path = os.path.dirname(sys.modules[__name__].__file__)
        path = os.path.join(path, "logo.jpg")
        
        f = open(path)
        #f.filename  = path
        portal = self.portal        
        self.portal.test_img.setImage(f)
        f.close()
        self.logout()

        
        # Reload Plone skins
        self._refreshSkinData()
        
    def test_resource_traverse(self):
        """ Check that we can extract width/height from resource based images """
        img  = "++resource++gomobile.mobile/phone_back.png" 
        portal = self.portal
        img_obj = portal.unrestrictedTraverse(img)
        
        util = getUtility(IImageInfoUtility)
        
        width, height = util.getImageInfo(img)

        # [386, 729]
        self.assertEqual(width, 386)
        self.assertEqual(height, 729)
        
    def test_skin_traverse(self):
        """ Check that we can extract width/height from Zope skin layer based images """        
        portal = self.portal
        img = "logo.jpg"
        util = getUtility(IImageInfoUtility)
        width, height = util.getImageInfo(img)
        
        # Note: This may vary on dependent theme products, so don't test
        #self.assertEqual(width, 100)
        #self.assertEqual(height, 44)
        
    def test_field_traverse(self):
        portal = self.portal
        img = "test_img/getImage"
        util = getUtility(IImageInfoUtility)
        width, height = util.getImageInfo(img)
        
        self.assertEqual(width, 252)
        self.assertEqual(height, 57)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestImageInfo))
    return suite
