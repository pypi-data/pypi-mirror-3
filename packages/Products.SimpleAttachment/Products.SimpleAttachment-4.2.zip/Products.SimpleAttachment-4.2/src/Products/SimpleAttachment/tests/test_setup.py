from Products.SimpleAttachment.tests.base import IntegrationTestCase


class TestInstallation(IntegrationTestCase):
    """Ensure product is properly installed"""

    def afterSetUp(self):
        self.css        = self.portal.portal_css
        self.tiny       = self.portal.portal_tinymce
        self.skins      = self.portal.portal_skins
        self.types      = self.portal.portal_types
        self.factory    = self.portal.portal_factory
        self.workflow   = self.portal.portal_workflow
        self.properties = self.portal.portal_properties

        self.metaTypes = ('ImageAttachment', 'FileAttachment')

    def testSkinLayersInstalled(self):
        self.failUnless('attachment_widgets' in self.skins.objectIds())
        self.failUnless('simpleattachment' in self.skins.objectIds())

    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.failUnless(t in self.types.objectIds())

    def testTypesNotSearched(self):
        types_not_searched = self.properties.site_properties.getProperty('types_not_searched')
        self.failUnless('FileAttachment' in types_not_searched)
        self.failUnless('ImageAttachment' in types_not_searched)

    def testTypesUseViewActionInListings(self):
        typesUseViewActionInListings = self.properties.site_properties.getProperty('typesUseViewActionInListings')
        self.failUnless('FileAttachment' in typesUseViewActionInListings)
        self.failUnless('ImageAttachment' in typesUseViewActionInListings)

    def testAttachmentsHaveNoWorkflow(self):
        self.assertEqual(self.workflow.getChainForPortalType('FileAttachment'), ())
        self.assertEqual(self.workflow.getChainForPortalType('ImageAttachment'), ())

    def testTinyResources(self):
        linkable = self.tiny.linkable.split('\n')
        imageobjects = self.tiny.imageobjects.split('\n')
        self.failUnless('FileAttachment' in linkable)
        self.failUnless('ImageAttachment' in linkable)
        self.failUnless('ImageAttachment' in imageobjects)


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
