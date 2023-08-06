__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.convergence.tests.base import ViewTestCase
from gomobile.convergence.browser import tabs

class TestTabs(ViewTestCase):

    def test_is_our_view(self):
        """ Check that the traversed object is ours.

        This means that our convergence browser layer has been succesfully applied on the
        HTTP request.
        """
        view = self.portal.restrictedTraverse("@@portal_tabs_view")
        self.assertTrue(isinstance(view, tabs.CatalogNavigationTabs))

    def test_query(self):
        """ Test brain content media retrofitting """
        self.create_sample_structure()
        self.loginAsPortalOwner()
        from gomobile.convergence.interfaces import IConvergenceMediaFilter
        filter= getUtility(IConvergenceMediaFilter)

        all_brains = self.portal.portal_catalog({"portal_type" : "Document"})
        result = filter.solveCatalogBrainContenMedia(self.portal, all_brains)

    def test_tabs_view(self):

        self.create_sample_structure()

        def hasTab(tabs, name):
            for t in tabs:
                if t["name"] == name:
                    return True

            return False

        self.setDiscriminateMode("web")
        view = self.portal.restrictedTraverse("@@portal_tabs_view")
        tabs = view.topLevelTabs()

        self.assertTrue(hasTab(tabs, "Web tree"))
        self.assertTrue(hasTab(tabs, "Generic tree"))
        self.assertFalse(hasTab(tabs, "Mobile tree"))


        self.setDiscriminateMode("mobile")
        view = self.portal.restrictedTraverse("@@portal_tabs_view")
        tabs = view.topLevelTabs()
        self.assertFalse(hasTab(tabs, "Web tree"))
        self.assertTrue(hasTab(tabs, "Generic tree"))
        self.assertTrue(hasTab(tabs, "Mobile tree"))

        self.loginAsPortalOwner()
        self.setDiscriminateMode("admin")
        tabs = view.topLevelTabs()
        self.assertTrue(hasTab(tabs, "Web tree"))
        self.assertTrue(hasTab(tabs, "Generic tree"))
        self.assertTrue(hasTab(tabs, "Mobile tree"))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTabs))
    return suite
