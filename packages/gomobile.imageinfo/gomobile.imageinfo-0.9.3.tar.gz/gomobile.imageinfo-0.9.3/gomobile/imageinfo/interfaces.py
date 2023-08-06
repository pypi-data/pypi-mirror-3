__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import zope.interface
from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager

class IImageInfoUtility(zope.interface.Interface):
    """ Helper class to deal with image metainfo based on traversing """

    def getImageInfo(path, timestamp):
        """
        
        @param path: Site root based graph traversing path to the image. Can be ++resource prefixed file system resource or ZODB image.
        
        @param timestamp: (optional) Unique string to identify image revision. If image data changes in path, different timestamp can be 
                          used to invalidate the cached version.
        
        @return: tuple (width, height)
        """
    

