"""Definition of the Image Gallery content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from xhostplus.gallery import galleryMessageFactory as _
from xhostplus.gallery.interfaces import IImageGallery
from xhostplus.gallery.config import PROJECTNAME

ImageGallerySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.BooleanField('slideshow',
        languageIndependent=1,
        widget=atapi.BooleanWidget(
              label=_(u'Enable slideshow'),
              description=_(u"Whether the slideshow is enabled or not."),
        ),
        required=False,
        searchable=False,
        default=False,
    ),

    atapi.IntegerField('slideshow_interval',
        languageIndependent=1,
        widget=atapi.IntegerWidget(
              label=_(u'Slideshow interval'),
              description=_(u"Seconds to wait for switching to the next image."),
        ),
        required=True,
        searchable=False,
        default=5,
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ImageGallerySchema['title'].storage = atapi.AnnotationStorage()
ImageGallerySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ImageGallerySchema,
    folderish=True,
    moveDiscussion=False
)

class ImageGallery(folder.ATFolder):
    """An image gallery folder"""
    implements(IImageGallery)

    meta_type = "Image Gallery"
    schema = ImageGallerySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def validate_slideshow_interval(self, value):
        try:
            value = int(value)
        except ValueError:
            return _(u"The interval time should be an integer.")
        if value < 1:
            return _(u"The interval time should not be lower than 1.")
        if value > 30:
            return _(u"The interval time should not be greater than 30.")
        return None

atapi.registerType(ImageGallery, PROJECTNAME)
