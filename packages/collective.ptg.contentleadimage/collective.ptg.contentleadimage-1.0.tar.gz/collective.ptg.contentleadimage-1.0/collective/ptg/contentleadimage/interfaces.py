from collective.plonetruegallery.interfaces import IBasicAdapter, IBaseSettings


class IContentLeadImageAdapter(IBasicAdapter):
    """
        Use plone to manage images directly, but show also items with
        contentleadimage.
    """

class IContentLeadImageGallerySettings(IBaseSettings):
    pass
