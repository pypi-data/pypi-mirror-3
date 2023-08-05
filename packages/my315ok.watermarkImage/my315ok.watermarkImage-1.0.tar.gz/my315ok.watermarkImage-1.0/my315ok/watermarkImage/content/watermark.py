"""Definition of the watermark content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.image import ATImage

from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf

from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED
from my315ok.watermarkImage import watermarkImageMessageFactory as  _
validation.register(MaxSizeValidator('checkImageMaxSize',
                                     maxsize=zconf.ATImage.max_file_size))


watermarkSchema = ATContentTypeSchema.copy() + atapi.Schema((
    atapi.ImageField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               storage = atapi.AnnotationStorage(migrate=True),
               swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
               pil_quality = zconf.pil_config.quality,
               pil_resize_algo = zconf.pil_config.resize_algo,
               max_size = zconf.ATImage.max_image_dimension,
               sizes ={},
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkImageMaxSize', V_REQUIRED)),
               widget = atapi.ImageWidget(
                        description = '',
                        label= _(u'watermark_image', default=u'Watermark Image'),
                        show_content_type = False,)),

    ), marshall=atapi.PrimaryFieldMarshaller()
    )

# -*- Message Factory Imported Here -*-

from my315ok.watermarkImage.interfaces import Iwatermark
from my315ok.watermarkImage.config import PROJECTNAME



# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

watermarkSchema['title'].storage = atapi.AnnotationStorage()
watermarkSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(watermarkSchema, moveDiscussion=False)


class watermark(ATImage):
    """a watermark image based ATImage"""
    implements(Iwatermark)

    meta_type = "watermark"
    schema = watermarkSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(watermark, PROJECTNAME)
