"""Definition of the SimpleReference content type
"""

from Products.ATContentTypes.content import schemata
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.SimpleReference import SimpleReferenceMessageFactory as _
from Products.SimpleReference.config import PROJECTNAME
from Products.SimpleReference.interfaces import IImageReference
from zope.interface import implements
from Products.ATContentTypes.content.image import ATImage, ATImageSchema
from Products.ATContentTypes.content.base import ATCTFileContent


ImageReferenceSchema = ATImageSchema.copy() + atapi.Schema((

    atapi.ReferenceField("image",
        title=_(u"Image Reference"),
        relationship='image_reference',
        allowed_types=('Image',),
        required=True,
        primary=True,
        languageIndependent=True,
        keepReferencesOnCopy=True,
        widget=ReferenceBrowserWidget,
    ),

))

ImageReferenceSchema['title'].storage = atapi.AnnotationStorage()
ImageReferenceSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(ImageReferenceSchema, moveDiscussion=False)


class ImageReference(ATImage):
    """Reference Item for RichDocument"""
    implements(IImageReference)

    meta_type = "ImageReference"
    schema = ImageReferenceSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def setImage(self, value, **kwargs):
        """ Hook for setImage
            do not upload any data because we are a reference
        """

        # set value (=UID) to image field
        self.getField('image').set(self,value)

        # set title here, because no one could set it before
        self.setTitle('Image reference: %s' % self.getImage().Title())

    def get_size(self):
        """ return size of reference = 0
        """
        return 0

    def tag(self, **kwargs):
        """ Generate image tag using the api of the ImageField of the
            referenced image
        """
        ref_obj = self.getImage()

        if ref_obj:
            return ref_obj.getField('image').tag(ref_obj, **kwargs)

        return 'this image has been deleted!'

    def __bobo_traverse__(self, REQUEST, name):
        """ Transparent access to referenced image scales
        """
        if name.startswith('image'):
            ref_obj = self.getImage()

            if ref_obj:
                field = ref_obj.getField('image')
                image = None
                if name == 'image':
                    image = field.getScale(ref_obj)
                else:
                    scalename = name[len('image_'):]
                    if scalename in field.getAvailableSizes(ref_obj):
                        image = field.getScale(ref_obj, scale=scalename)
                if image is not None and not isinstance(image, basestring):
                    # image might be None or '' for empty images
                    return image
            else:
                return 'this image has been deleted!'

        return ATCTFileContent.__bobo_traverse__(self, REQUEST, name)


atapi.registerType(ImageReference, PROJECTNAME)



