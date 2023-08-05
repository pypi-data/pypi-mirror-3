"""Definition of the Intro page content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED

from xhostplus.intropage import intropageMessageFactory as _

from xhostplus.intropage.interfaces import IIntropage
from xhostplus.intropage.config import PROJECTNAME

IMAGE_FORMATS = (
    'image/gif',
    'image/jpeg',
    'image/png',
)

IntropageSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.ImageField('image',
                required = True,
                languageIndependent = False,
                swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
                pil_quality = zconf.pil_config.quality,
                pil_resize_algo = zconf.pil_config.resize_algo,
                max_size = zconf.ATImage.max_image_dimension,
                allowable_content_types=IMAGE_FORMATS,
                validators = (
                    ('isNonEmptyFile', V_REQUIRED),
                ),
                widget = atapi.ImageWidget(
                     description = _(u"The image to display on the intro page"),
                     label= _(u"Image"),
                     show_content_type = False,
                ),
                storage=atapi.AttributeStorage(),
    ),

    atapi.StringField('link',
            required = True,
            languageIndependent = False,
            widget = atapi.StringWidget(
                description = _(u"The page URL the image should link to"),
                label = _(u"Link"),
            )
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

IntropageSchema['title'].storage = atapi.AnnotationStorage()
IntropageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(IntropageSchema, moveDiscussion=False)


class Intropage(base.ATCTContent):
    """A intro page"""
    implements(IIntropage)

    meta_type = "Intropage"
    schema = IntropageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Intropage, PROJECTNAME)
