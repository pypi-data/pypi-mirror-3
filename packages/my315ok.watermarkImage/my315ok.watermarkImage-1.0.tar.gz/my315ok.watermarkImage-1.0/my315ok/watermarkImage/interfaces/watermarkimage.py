from zope.interface import Interface
from Products.ATContentTypes.interface import IATImage
# -*- Additional Imports Here -*-


#class IWatermarkImage(Interface):
class IWatermarkImage(IATImage):
    """watermark image content type"""

    # -*- schema definition goes here -*-

from plone.theme.interfaces import IDefaultPloneLayer

class ISiteWatermarkpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
class IImageInfoUtility(Interface):
    """ Helper class to deal with image metainfo based on traversing """

    def getImageInfo(path, timestamp):
        """
        
        @param path: Site root based graph traversing path to the image. Can be ++resource prefixed file system resource or ZODB image.
        
        @param timestamp: (optional) Unique string to identify image revision. If image data changes in path, different timestamp can be 
                          used to invalidate the cached version.
        
        @return: tuple (width, height)
        """
