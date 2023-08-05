"""Definition of the WatermarkImage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from my315ok.watermarkImage.interfaces import IWatermarkImage
from my315ok.watermarkImage.config import PROJECTNAME

from Products.ATContentTypes.content.image import ATImage
from my315ok.watermarkImage.watermarkfield import WatermarkImageField as  ImageField
from my315ok.watermarkImage import watermarkImageMessageFactory as  _
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf

from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

validation.register(MaxSizeValidator('checkImageMaxSize',
                                     maxsize=zconf.ATImage.max_file_size))


WatermarkImageSchema = ATContentTypeSchema.copy() + atapi.Schema((
    ImageField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               storage = atapi.AnnotationStorage(migrate=True),
               swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
               pil_quality = zconf.pil_config.quality,
               pil_resize_algo = zconf.pil_config.resize_algo,
               max_size = zconf.ATImage.max_image_dimension,
               sizes= {'large'   : (768, 768),
                       'preview' : (400, 400),
                       'mini'    : (200, 200),                   
                      },
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkImageMaxSize', V_REQUIRED)),
               widget = atapi.ImageWidget(
                        description = '',
                        label= _(u'image_attach_watermark', default=u'Image'),
                        show_content_type = False,)),

    ), marshall=atapi.PrimaryFieldMarshaller()
    )

# Title is pulled from the file name if we don't specify anything,
# so it's not strictly required, unlike in the rest of ATCT.
WatermarkImageSchema['title'].required = False




# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

WatermarkImageSchema['title'].storage = atapi.AnnotationStorage()
WatermarkImageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(WatermarkImageSchema, moveDiscussion=False)


class WatermarkImage(ATImage):
    """watermark image content type"""
    implements(IWatermarkImage)

    meta_type = "WatermarkImage"
    schema = WatermarkImageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(WatermarkImage, PROJECTNAME)
