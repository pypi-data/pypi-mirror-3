"""Definition of the Picture Folder content type
"""

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED
from Products.CMFCore.permissions import View

from xhostplus.picturefolder import picturefolderMessageFactory as _

from xhostplus.picturefolder.interfaces import IPictureFolder
from xhostplus.picturefolder.config import PROJECTNAME

# Possible image formats
IMAGE_FORMATS = (
    'image/gif',
    'image/jpeg',
    'image/png',
)

# Possible values for image alignment
IMAGE_ALIGNMENTS = atapi.DisplayList((
    ('left', _('Left aligned')),
    ('right', _('Right aligned')),
))

PictureFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.ImageField('image',
                required = False,
                languageIndependent = True,
                swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
                pil_quality = zconf.pil_config.quality,
                pil_resize_algo = zconf.pil_config.resize_algo,
                max_size = zconf.ATImage.max_image_dimension,
                allowable_content_types=IMAGE_FORMATS,
                sizes= {
                    'large'   : (768, 768),
                    'preview' : (400, 400),
                    'mini'    : (200, 200),
                    'thumb'   : (128, 128),
                    'tile'    :   (64, 64),
                    'icon'    :   (32, 32),
                    'listing' :   (16, 16),
                },
                validators = (
                    ('isNonEmptyFile', V_REQUIRED),
                ),
                widget = atapi.ImageWidget(
                     description = _(u"The image for the folder"),
                     label= _(u"Image"),
                     show_content_type = False,
                ),
                storage=atapi.AttributeStorage(),
    ),

    atapi.StringField('imageCaption',
        required = False,
        languageIndependent = False,
        searchable = True,
        widget = atapi.StringWidget(
            description = "",
            label = _(u"Image Caption"),
            size = 40
        )
    ),

    atapi.StringField('alignment',
        required = True,
        languageIndependent = True,
        searchable = False,
        vocabulary = IMAGE_ALIGNMENTS,
        default = 'right',
        widget = atapi.SelectionWidget(
            label = _(u"Alignment"),
            description = _(u"The alignment of the image in the folder listing"),
        ),
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PictureFolderSchema['title'].storage = atapi.AnnotationStorage()
PictureFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    PictureFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class PictureFolder(folder.ATFolder):
    """A folder with an image field"""
    implements(IPictureFolder)

    meta_type = "PictureFolder"
    schema = PictureFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security = ClassSecurityInfo()

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        html_class = self.getAlignment() == 'left' and 'tileImageLeft' or 'tileImageRight'
        
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        if 'css_class' not in kwargs:
            kwargs['css_class'] = html_class
        else:
            kwargs['css_class'] += " %s" % html_class
        return self.getField('image').tag(self, **kwargs)

atapi.registerType(PictureFolder, PROJECTNAME)
