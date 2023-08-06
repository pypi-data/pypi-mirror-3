from zope.interface import implements
from zope.component import adapts, getMultiAdapter

from plone.memoize.instance import memoize

from Products.ATContentTypes.interface.image import IImageContent
from Products.ATContentTypes.interface import IATTopic
from Products.Archetypes.interfaces import IBaseFolder
from Products.CMFCore.utils import getToolByName

from collective.plonetruegallery.galleryadapters.base import BaseAdapter, BaseImageInformationRetriever
from collective.plonetruegallery.galleryadapters.basic import BasicAdapter
from collective.plonetruegallery.interfaces import IImageInformationRetriever, IGalleryAdapter, IBasicGallerySettings


from collective.contentleadimage.interfaces import ILeadImageable
from collective.contentleadimage.config import IMAGE_FIELD_NAME

from .interfaces import IContentLeadImageAdapter, IContentLeadImageGallerySettings


class ContentLeadImageAdapter(BasicAdapter):
    """ Just the basic class works, just define own interfaces """
    implements(IContentLeadImageAdapter, IGalleryAdapter)
    name = "contentleadimage"
    description = "Use Plone, ContentLeadImages enabled"

    schema = IContentLeadImageGallerySettings


class ContentLeadImageBaseImageInformationRetriever(BaseImageInformationRetriever):
    def get_image_url(self, image):
        size = self.gallery_adapter.size_map[self.gallery_adapter.settings.size]
        if image.hasContentLeadImage:
            field_path = IMAGE_FIELD_NAME
        else:
            field_path = 'image'
        return "%s/%s_%s" % (image.getURL(), field_path, size)

    def get_thumb_url(self, image):
        size = self.gallery_adapter.settings.thumb_size
        if not size:
            size = 'tile'
        if image.hasContentLeadImage:
            field_path = IMAGE_FIELD_NAME
        else:
            field_path = 'image'
        return "%s/%s_%s" % (image.getURL(), field_path, size)


class ContentLeadImageImageInformationRetriever(ContentLeadImageBaseImageInformationRetriever):
    implements(IImageInformationRetriever)
    adapts(IBaseFolder, IContentLeadImageAdapter)

    def getImageInformation(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        gallery_path = self.context.getPhysicalPath()
        images = catalog.searchResults(
            object_provides={'query':[IImageContent.__identifier__,
                                      ILeadImageable.__identifier__],
                             'operator': 'or'},
            path='/'.join(gallery_path),
            sort_on='getObjPositionInParent'
        )
        
        # filter out image images that are not directly in its path and LeadImageables without image
        def filterfunc(i):
            inPath = len(i.getPath().split('/')) == len(gallery_path) + 1 
            hasImage = i.hasContentLeadImage is not False
            return inPath and hasImage
        images = filter(filterfunc, images)
        return map(self.assemble_image_information, images)


class ContentLeadImageTopicImageInformationRetriever(ContentLeadImageBaseImageInformationRetriever):
    implements(IImageInformationRetriever)
    adapts(IATTopic, IContentLeadImageAdapter)

    def getImageInformation(self):
        query = self.context.buildQuery()
        if query is not None:
            query.update({'object_provides': {
                            'query':[IImageContent.__identifier__,
                                     ILeadImageable.__identifier__],
                            'operator': 'or'}})
            catalog = getToolByName(self.context, 'portal_catalog')
            images = catalog(query)
            filterfunc = lambda i: i.hasContentLeadImage in (True, None)
            images = filter(filterfunc, images)
            return map(self.assemble_image_information, images)
        else:
            return []
