from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.SimpleReference.browser.interfaces import IImageControls, \
    IFileControls, IViewletFileListing, IViewletImageListing
from zope.component import getMultiAdapter


class Reference(BrowserView):
    """ functions for reference browser popup
    """

    def search_types(self):
        req_type = self.request.get('type')
        return (req_type, 'Folder')

    def linkable_types(self):
        req_type = self.request.get('type')
        return (req_type, )

    def browseable_types(self):
        return ('Folder', )

    def add_reference(self, uid):
        """
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context,self.request),
                                       name="plone_portal_state")
        portal = portal_state.portal()
        refcat = getToolByName(portal, 'reference_catalog')

        at_obj = refcat.lookupObject(uid)
        if at_obj:
            ref_type = '%sReference' % at_obj.portal_type
            at_obj_id = context.generateUniqueId(ref_type)
            new_id = context.invokeFactory(
                        id=at_obj_id,
                        type_name=ref_type
                     )

            new_obj = getattr(context, new_id)

            if ref_type=='ImageReference':
                new_obj.setImage(uid)
                IVManager = IImageControls
                IViewlet = IViewletImageListing
                vmanager_name = 'simpleattachment.imagecontrols'
                viewlet_name = 'simpleattachment.imagelisting'
            else:
                new_obj.setFile(uid)
                IVManager = IFileControls
                IViewlet = IViewletFileListing
                vmanager_name = 'simpleattachment.filecontrols'
                viewlet_name = 'simpleattachment.filelisting'

            new_obj.reindexObject()

            # update controls viewletmanager and return html code
            viewlet_manager = getMultiAdapter((self.context,
                                               self.request,
                                               self, ),
                                              IVManager,
                                              name=vmanager_name )

            viewlet_manager.update()
            return viewlet_manager.render()

        return 'error!'
