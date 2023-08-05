'''
Created on 07.11.2011

@author: peterm
'''
from Products.ATContentTypes.content import schemata
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.SimpleReference import SimpleReferenceMessageFactory as _
from Products.SimpleReference.config import PROJECTNAME
from Products.SimpleReference.interfaces import IFileReference
from zope.interface import implements
from Products.ATContentTypes.content.file import ATFile, ATFileSchema


FileReferenceSchema = ATFileSchema.copy() + atapi.Schema((

    atapi.ReferenceField("file",
        title=_(u"File Reference"),
        relationship='file_reference',
        allowed_types=('File',),
        required=True,
        primary=True,
        languageIndependent=True,
        keepReferencesOnCopy=True,
        widget=ReferenceBrowserWidget,
    ),

))

FileReferenceSchema['title'].storage = atapi.AnnotationStorage()
FileReferenceSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(FileReferenceSchema, moveDiscussion=False)


class FileReference(ATFile):
    """Reference Item for RichDocument"""
    implements(IFileReference)

    meta_type = "FileReference"
    schema = FileReferenceSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def index_html(self, REQUEST=None, RESPONSE=None):
        """ Download the file
        """
        return self.download()

    def download(self, REQUEST=None, RESPONSE=None):
        """ Download the file (use default index_html)
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        ref_file = self.getFile()

        if ref_file:
            ref_file_field = ref_file.getPrimaryField()
            return ref_file_field.download(ref_file, REQUEST, RESPONSE)
        else:
            return None

    def setFile(self, value, **kwargs):
        """ Hook for setFile
            do not upload any data because we are a reference
        """

        # set value (=UID) to file field
        self.getField('file').set(self,value)

        # set title here, because no one could set it before
        self.setTitle('File reference: %s' % self.getFile().Title())

    def get_size(self):
        """ return size of reference = 0
        """
        if self.getFile():
            return self.getFile().get_size()
        else:
            return 0

    def getIcon(self,relative_to_portal=False):
        """ wrapper for getIcon
            return icon of reference
        """
        if self.getFile():
            return self.getFile().getIcon(relative_to_portal)


atapi.registerType(FileReference, PROJECTNAME)
