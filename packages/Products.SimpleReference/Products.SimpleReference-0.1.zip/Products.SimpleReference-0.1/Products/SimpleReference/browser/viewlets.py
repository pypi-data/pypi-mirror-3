from Acquisition import aq_inner
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from interfaces import IViewletImageListing, IViewletFileListing

class ImageListing(ViewletBase):
    """
    """
    
    implements(IViewletImageListing)
    render = ViewPageTemplateFile('templates/imagelisting.pt')
    
    def get_images(self):
        """
        """
        context = aq_inner(self.context)
        return context.getFolderContents({'portal_type':['ImageAttachment',
                                                         'ImageReference']},
                                         full_objects=True)
                                         
                                         
class FileListing(ViewletBase):
    """
    """
    
    implements(IViewletFileListing)
    render = ViewPageTemplateFile('templates/filelisting.pt')
    
    def get_files(self):
        """
        """
        context = aq_inner(self.context)
        return context.getFolderContents({'portal_type':['FileAttachment',
                                                         'FileReference']},
                                         full_objects=True)

    