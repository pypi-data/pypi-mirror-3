"""

    Tools to manipulate any kind of Zope images using PIL.

    http://mfabrik.com

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__docformat__ = "epytext"
__author__ = "Mikko Ohtamaa"

import urlparse
import urllib2
import cStringIO

import PIL
from PIL.ImageFile import ImageFile
import zope.interface

import OFS
from AccessControl import Unauthorized
from Products.CMFCore.FSImage import FSImage
from Products.Archetypes.Field import Image as ATFieldImage
from Products.ATContentTypes.interface import IATImage
from Products.Five.browser import BrowserView

from zope.app.component.hooks import getSite
from zope.component import getUtility, queryUtility

from gomobile.imageinfo.interfaces import IImageInfoUtility

try:
    from plone.app.blob.field import BlobWrapper
    HAS_BLOBS = True
except ImportError:
    HAS_BLOBS = False

class ImageInfoUtility(object):
    """ Unified interface to access different Zope image objects

    Return PIL presentation of images

    - Skin layer images, both file system based and ZMI uploads

    - Archetypes ATImage

    - Resource images (static media, available through ZCML resourceDirectory directive)

    """

    zope.interface.implements(IImageInfoUtility)

    def __init__(self):
        # path + timestamp -> [width, height] mappings
        # TODO: Cache is never flushed
        self.cache = {}

    def generateCacheKey(self, path, timestamp):
        if not timestamp:
            timestamp = ""

        return path + timestamp

    def getImageInfo(self, path, timestamp=None):
        """ Get image width and height based on image traversing path on the site.

        FS and ZODB based images are equally supported.

        Optional timestamp parameter can be supplied. Timestamp is an external key which
        knowns when the image was last changed. This is an issue for ATImages
        which the user can change themselves. We need to purge the cache after ATImage has been changed.

        TODO: Is it possible to fetch timestamp information from the image objects themselves in reliable manner?

        @param path: Site root based graph traversing path to the image. Can be ++resource prefixed file system resource or ZODB image.

        @param timestamp: Unique string to identify image revision. If image data changes in path, different timestamp can be
                          used to invalidate the cached version. Optional. None to cache the information during the whole process life cycle.

        @return: tuple (width, height)
        """

        key = self.generateCacheKey(path, timestamp)
        if not key in self.cache:
            info = self.fetchInfo(path)
            self.cache[key] = info

        return self.cache[key]

    def fetchInfo(self,  path):
        """ Traverse to image and extract.

        Supports FS and ZODB based images. FS based images are read using PIL.
        """


        img =  self.getImageObject(path)

        if isinstance(img, ImageFile):
            return img.size
        else:
            return [img.width, img.height]

    def getImageObject(self, path):
        """ Get image handle to traversable Zope object, assuming object is some sort of image

        Path must not start with slash.
        Path is relative to the site root.

        @param path: Path to Zope object

        @return: Image-like object (heterogenous return values)
        """
        site = getSite()

        try:
            img = site.unrestrictedTraverse(path)
        except Unauthorized:
            # The parent folder might be private and the image public,
            # in which case we should be able to view the image after all.
            parent_path = '/'.join(path.split('/')[:-1])
            image_path = path.split('/')[-1]
            parent = site.unrestrictedTraverse(parent_path)
            img = parent.restrictedTraverse(image_path)


        # UGH... the resource based image isn't a real class but some
        # dynamically generated Five metaclass... no fucking clue
        # how to do interface checks against those,
        # so we just
        if ("DirContainedImageResource" in img.__class__.__name__) or ("FileResource" in img.__class__.__name__) :
            # Resource based image, on file system, handle with PIL
            # info = (width, height)
            source = img.context.path
            info = PIL.Image.open(source)
            return info
        elif isinstance(img, FSImage):
            # FSImage at /plone/logo
            # width, height = util.getImageInfo(img)
            # <implementedBy Products.CMFCore.FSImage.FSImage>
            return img
        elif isinstance(img, OFS.Image.Image):
            # image uploaded to a portal_skins/custom
            return img
        elif IATImage.providedBy(img):
            # Image is uploaded image content type
            return img.getImage()
        else:

            # pointer to exposed ATImage method
            if callable(img):
                img = img()

            if HAS_BLOBS:
                # img might be <bound method ATBlob.getImage of <ATImage at /plone/test_img>
                # We resolve it to blob above
                if isinstance(img, BlobWrapper):
                    return img

            if isinstance(img, ATFieldImage):
                return img


            raise RuntimeError("Unknown image object %s:%s" % (path, str(img.__class__)))

        return info

    def downloadImage(self, url):
        """ Get remote image data and store.
        """
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
            data = response.read()
        except Exception, e:
            # Downlaod error, HTTP parse error, socket io error, ect.
            return None

        io = cStringIO.StringIO(data)
        return PIL.Image.open(io)


    def getOrDownloadImageObject(self, url):
        """ Get Zope internal or external image object.

        @param: http:// URL or Zope path
        """

        if "//" in url:
            return self.downloadImage(url)
        else:
            return self.getPILFromPath(url)


    def getPILFromObject(self, obj):
        """ Convert various Zope based image objects to Python Imaging Library image data.

        @param obj: Any Zope imagish object
        """

        if isinstance(obj, ImageFile):
            # Normal file system file
            return obj
        elif isinstance(obj, FSImage):
            # FSImage
            # Read data from object
            return PIL.Image.open(obj.getObjectFSPath())
        elif isinstance(obj, ATFieldImage):
            # Read data from object
            pimage = obj.data

            # TODO
            # Not sure what's going on here...
            #
            if hasattr(pimage, "data"):
                data = pimage.data
            else:
                data = pimage

            io = cStringIO.StringIO(data)
            return PIL.Image.open(io)
        elif IATImage.providedBy(obj):
            obj = obj.getImage()
            data = obj.data
            io = cStringIO.StringIO(data)
            return PIL.Image.open(io)
        elif isinstance(obj, OFS.Image.Image):
            # OFS Image
            # Held in the portal_skins folder, uploaded via ZMI
            data = obj.data
            io = cStringIO.StringIO(data)
            return PIL.Image.open(io)
        elif HAS_BLOBS and isinstance(obj, BlobWrapper):
            # Plone 4 BLOB images
            data = obj.data
            io = cStringIO.StringIO(data)
            return PIL.Image.open(io)
        else:
            raise RuntimeError("Can't handle:" + str(obj))

    def getPILFromPath(self, path):
        """ Return Python Imaging Library manipulation object

        @param path: Zope traversing path
        @return: PIL manipulation object
        """
        obj = self.getImageObject(path)
        return self.getPILFromObject(obj)

    def performResize(self, image, w, h, conserve_aspect_ration=True):
        """ Return resized

        @param image: PIL image object

        @param conserve_aspect_ration: Do not stretch image

        @param return: [Image data, format]
        """
        default_format = "PNG"

        pil_quality = 88

        # Extract the orignal image format from data
        format = image.format
        if format == None:
            format = default_format

        # consider image mode when scaling
        # source images can be mode '1','L,','P','RGB(A)'
        # convert to greyscale or RGBA before scaling
        # preserve palletted mode (but not pallette)
        # for palletted-only image formats, e.g. GIF
        # PNG compression is OK for RGBA thumbnails
        original_mode = image.mode
        if original_mode == '1':
            image = image.convert('L')
        elif original_mode == 'P':
            image = image.convert('RGBA')

        if conserve_aspect_ration:
            image.thumbnail([w,h], PIL.Image.ANTIALIAS)
        else:
            # FAUDSFASDF ASF ASDF"#
            # PIL has different API for image.thumbnail and resize
            # Now give me vodka....
            image = image.resize([w,h], PIL.Image.ANTIALIAS)


        # decided to only preserve palletted mode
        # for GIF, could also use image.format in ('GIF','PNG')
        if original_mode == 'P' and format == 'GIF':
            image = image.convert('P')
        thumbnail_file = cStringIO.StringIO()
        # quality parameter doesn't affect lossless formats

        image.save(thumbnail_file, format, quality=pil_quality)
        thumbnail_file.seek(0)
        return thumbnail_file, format.lower()

    def getResizedImage(self, path, w, h, conserve_aspect_ration=True):
        """ Return resized image payload and its format.

        Format is PIL format string: GIF, PNG or JPG.

        @param path: Zope traversing path to the image

        @param conserve_aspect_ration: Do not stretch image

        @param return: [Image data, format]
        """
        image = self.getPILFromPath(path)
        return self.performResize(image, w, h, conserve_aspect_ration)

    def resizeImage(self, obj, w, h, conserve_aspect_ration=True):
        """ Return resized image payload and its format.

        Format is PIL format string: GIF, PNG or JPG.

        @param obj: Any image-like Zope object

        @param conserve_aspect_ration: Do not stretch image

        @param return: [Image data, format]
        """
        image = self.getPILFromObject(obj)
        return self.performResize(image, w, h, conserve_aspect_ration)


    def getURLResizedImage(self, path, w, h, conserve_aspect_ration=True):
        """ Return resized image payload and its format.

        Format is PIL format string: GIF, PNG or JPG.
        Path can be full URL. If the image download fails,
        None is returned.

        @param path: Zope traversing path to the image or http:// URL to the image

        @param conserve_aspect_ration: Do not stretch image

        @param return: [Image data, format] or [None, None] if image data is not available
        """
        image = self.getOrDownloadImageObject(path)

        if image is None:
            return (None, None)

        return self.performResize(image, w, h, conserve_aspect_ration)




