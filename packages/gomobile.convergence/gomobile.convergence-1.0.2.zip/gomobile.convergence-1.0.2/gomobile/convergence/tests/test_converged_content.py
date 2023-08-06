"""


"""

__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.convergence.tests.base import BaseTestCase
from gomobile.convergence.interfaces import ContentMediaOption, IConvergenceMediaFilter


class TestConvergence(BaseTestCase):
    """ Check setting content media options, folder listing filtering and navigation tree building options. """

    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)


    def test_has_catalog_index(self):
        """ Check that media options are indexed properly """
        catalog = self.portal.portal_catalog
        self.assertTrue("getContentMedias" in catalog.indexes())
        self.assertTrue("getContentMedias" in catalog.schema())
        self.create_sample_structure()
        res = catalog({"portal_type" : "Document"})


    def test_list_mixed_root_folder(self):
        """ Both web and mobile and shared items in a folder. """

        sample_folder = self.create_sample_structure()

        # Anonymous mobile visitor
        self.setDiscriminateMode("mobile")
        listing = sample_folder.listFolderContents()

        # We should have mobile_tree, generic_tree, mobile_doc
        self.assertEqual(len(listing), 7)

        # Anonymous web visitor
        self.setDiscriminateMode("web")
        # In root folder, two web items
        listing = sample_folder.listFolderContents()
        self.assertEqual(len(listing), 7)


    def test_acquire_parent_folder_content_media(self):

        sample_folder = self.create_sample_structure()
        self.setDiscriminateMode("mobile")
        # Check that mobile acquisition works
        listing = sample_folder.mobile_tree.listFolderContents()
        self.assertEqual(len(listing), 2)

    def test_acquire_parent_folder_content_media_no_items(self):
        """ Web has no items in mobile only folder """

        sample_folder = self.create_sample_structure()

        # See that items are clearly marked as mobile
        media = self.filter.solveContentMedia(sample_folder.mobile_tree.mobile_tree_inside_1)
        self.assertEqual(media, ContentMediaOption.MOBILE)

        media = self.filter.solveContentMedia(sample_folder.mobile_tree)
        self.assertEqual(media, ContentMediaOption.MOBILE)

        # Go web
        self.setDiscriminateMode("web")
        listing = sample_folder.mobile_tree.listFolderContents()
        # Web guy should have zero items
        self.assertEqual(len(listing), 0)

    def test_admin_list_folder(self):
        """ Admin sees all items whether they are mobile or not """
        sample_folder = self.create_sample_structure()
        self.loginAsPortalOwner()

        # Now we are admin in web, see everything
        self.setDiscriminateMode("admin")

        listing = sample_folder.listFolderContents()
        self.assertEqual(len(listing), 9)

        # But admin in mobile should not see non-mobile content
        self.setDiscriminateMode("mobile")
        listing = sample_folder.listFolderContents()
        self.assertEqual(len(listing), 7)

    def test_build_sitemap(self):
        """ Test that content media acquisition works correctly in navigation trees and sitemaps.

        See that admin sees the full sitemap properly.
        """
        sample_folder = self.create_sample_structure()

        self.loginAsPortalOwner()
        self.setDiscriminateMode("admin")

        brains = self.portal.portal_catalog()
        data = self.filter.solveCatalogBrainContenMedia(self.portal, brains)
        #for brain, state in data.items():
        #    print brain.getURL() + " local:" + str(brain["getContentMedias"]) + " solved:" + str(state)

        data = self.getNavtreeData()

        # Check that sitemap data has media options set
        #for i in data:
        #    self.assertTrue("content_media" in i)

        # Check navigation tree output is sane

        e = self.getEntryByPath(data, "/mobile_tree")
        self.assertEqual(e["content_media"], "mobile")

        e = self.getEntryByPath(data, "/mobile_tree/mobile_tree_inside_1")
        self.assertEqual(e["content_media"], "mobile")

        e = self.getEntryByPath(data, "/generic_tree")
        self.assertEqual(e["content_media"], "both")

        e = self.getEntryByPath(data, "/generic_tree/generic_tree_inside_1")
        self.assertEqual(e["content_media"], "both")

        e = self.getEntryByPath(data, "/web_tree")
        self.assertEqual(e["content_media"], "web")

        e = self.getEntryByPath(data, "/web_tree/web_tree_inside_1")
        self.assertEqual(e["content_media"], "web")

    def test_sitemap_mobile_filtering(self):
        sample_folder = self.create_sample_structure()
        self.setDiscriminateMode("mobile")
        data = self.getNavtreeData()

        e = self.getEntryByPath(data, "/mobile_tree/mobile_tree_inside_1")

        try:
            e = self.getEntryByPath(data, "/web_tree")
            raise AssertionError("Should not be reached")
        except KeyError:
            pass

        e = self.getEntryByPath(data, "/generic_tree")

    def test_sitemap_web_filtering(self):
        sample_folder = self.create_sample_structure()
        self.setDiscriminateMode("web")
        data = self.getNavtreeData()

        e = self.getEntryByPath(data, "/web_tree/web_tree_inside_1")

        try:
            e = self.getEntryByPath(data, "/mobile_tree")
            raise AssertionError("Should not be reached")
        except KeyError:
            pass

        e = self.getEntryByPath(data, "/generic_tree")

    def test_set_bad_value(self):
        """
        """
        sample_folder = self.create_sample_structure()
        from zope.schema.interfaces import ConstraintNotSatisfied
        try:
            self.filter.setContentMedia(sample_folder.web_doc, "foobar")
            raise AssertionError("Should not be reached")
        except ConstraintNotSatisfied:
            pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConvergence))
    return suite
