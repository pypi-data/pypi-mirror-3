from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from xhostplus.gallery import galleryMessageFactory as _

class IImageGallery(Interface):
    """An image gallery folder"""
    
    # -*- schema definition goes here -*-
