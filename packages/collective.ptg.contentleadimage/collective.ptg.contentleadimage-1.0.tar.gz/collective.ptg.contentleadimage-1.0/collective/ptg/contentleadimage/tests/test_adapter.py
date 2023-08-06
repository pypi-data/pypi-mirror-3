import unittest
import os

from zope.testing import doctestunit
from zope.component import testing, getMultiAdapter, provideAdapter
from zope.publisher.browser import TestRequest
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from collective.plonetruegallery.config import named_adapter_prefix
from collective.plonetruegallery.meta.zcml import getAllGalleryTypes

from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.utils import hasContentLeadImage

ztc.installProduct('collective.plonetruegallery')
ztc.installProduct('collective.contentleadimage')
ptc.setupPloneSite(products=('collective.plonetruegallery',
                             'collective.contentleadimage'))


import collective.ptg.contentleadimage

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.ptg.contentleadimage)
            fiveconfigure.debug_mode = False
            #Force loading this indexer, it doesn't automatically
            provideAdapter(hasContentLeadImage, name='hasContentLeadImage')

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.setRoles(('Manager',))

        self.portal.invokeFactory(id="test_gallery", type_name="Folder")

        # Add 2 images
        for i in range(1, 3):
            self.portal['test_gallery'].invokeFactory(id=str(i), type_name="Image")
            self.portal['test_gallery'][str(i)].setDescription("Description for %i" % i)
            self.portal['test_gallery'][str(i)].setTitle("Title for %i" % i)
            self.portal['test_gallery'][str(i)].indexObject()

    def get_gallery(self):
        return self.portal['test_gallery']

    def get_contentleadimage_adapter(self):
        return getMultiAdapter(
            (self.get_gallery(), TestRequest()),
            name=named_adapter_prefix + 'contentleadimage'
        )

    def test_galery_type(self):
        galleries = getAllGalleryTypes()
        factory = collective.ptg.contentleadimage.adapters.ContentLeadImageAdapter
        self.assertTrue(factory in getAllGalleryTypes())

        adapter = getMultiAdapter(
                (self.get_gallery(), TestRequest()),
                name=named_adapter_prefix + 'contentleadimage'
        )
        self.failUnless(isinstance(adapter, factory))

    def test_all_images_found_in_folder(self):
        adapter = self.get_contentleadimage_adapter()
        self.failUnless(len(adapter.retrieve_images()) == 2)

        # Add a document with a leadimage
        self.get_gallery().invokeFactory(id='document_with_image', type_name="Document")
        document = self.get_gallery()['document_with_image']
        document.update(title="Title with image", description="Description with image")
        document.processForm()
        test_image = os.path.join(os.path.dirname(__file__),
                                  'test_41x41.jpg')
        raw_image = open(test_image, 'rb').read()
        field = document.getField(IMAGE_FIELD_NAME)
        field.set(document, raw_image)
        document.reindexObject(idxs=['hasContentLeadImage'])

        self.failUnless(len(adapter.retrieve_images()) == 3)

        # Add a document without a leadimage
        self.get_gallery().invokeFactory(id='document_without_image', type_name="Document")
        document = self.get_gallery()['document_without_image']
        document.setDescription("Description without image")
        document.setTitle("Title without image")
        #Ensure there is no image
        field = document.getField(IMAGE_FIELD_NAME)
        field.set(document, 'DELETE_IMAGE')
        document.reindexObject()
        document.reindexObject(idxs=['hasContentLeadImage'])

        self.failUnless(len(adapter.retrieve_images()) == 3)


def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestCase),

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='collective.ptg.contentleadimage',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='collective.ptg.contentleadimage.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.ptg.contentleadimage',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='collective.ptg.contentleadimage',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
