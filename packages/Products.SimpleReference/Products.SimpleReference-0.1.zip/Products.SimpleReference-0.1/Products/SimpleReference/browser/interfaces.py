from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager

class IViewletImageListing(Interface):
    """ marker interface for imagelisting viewlet
    """
    
class IViewletFileListing(Interface):
    """ marker interface for filelisting viewlet
    """

class IAboveListing(IViewletManager):
    """ Marker interface for viewlets that can be displayed in my custom header
        viewlet manager
    """

class IImageControls(IViewletManager):
    """ Marker interface for viewlets that can be displayed in my custom header
        viewlet manager
    """

class IFileControls(IViewletManager):
    """ Marker interface for viewlets that can be displayed in my custom header
        viewlet manager
    """
