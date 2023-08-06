__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.convergence.tests.base import ViewTestCase

from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

class TestSiteMap(ViewTestCase):

    def test_sitemap_view(self):

        self.create_sample_structure()

        view = self.portal.restrictedTraverse("@@sitemap_view")
        view.createSiteMap()

        self.setDiscriminateMode("web")
        view = self.portal.restrictedTraverse("@@sitemap_view")
        view.createSiteMap()

        self.setDiscriminateMode("mobile")
        view = self.portal.restrictedTraverse("@@sitemap_view")
        view.createSiteMap()

        # TODO: Check we  have items there
        self.loginAsPortalOwner()
        self.setDiscriminateMode("web")
        view = self.portal.restrictedTraverse("@@sitemap_view")
        view.createSiteMap()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSiteMap))
    return suite
