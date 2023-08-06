"""


    Test breadcrumbs in web and mobile hybrid mode.

"""

__license__ = "GPL 2"
__copyright__ = "2009-2010 mFabrik Research Oy"

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.convergence.tests.base import ViewTestCase
from gomobile.convergence.browser.breadcrumbs import PhysicalNavigationBreadcrumbs

class TestBreadcrumbs(ViewTestCase):

    def test_breadcrumb_view(self):

        self.create_sample_structure()
        
        self.setDiscriminateMode("web")
        view = PhysicalNavigationBreadcrumbs(self.portal.web_tree, self.portal.REQUEST)
        view.breadcrumbs()
                    
        self.setDiscriminateMode("mobile")
        view = PhysicalNavigationBreadcrumbs(self.portal.web_tree, self.portal.REQUEST)
        view.breadcrumbs()
            
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBreadcrumbs))
    return suite
