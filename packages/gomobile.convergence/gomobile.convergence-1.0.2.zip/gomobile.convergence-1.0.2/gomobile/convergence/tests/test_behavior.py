"""

    Test multi-channel behavior object.

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = "epytext" 

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.interfaces import IMobileContentish

from gomobile.convergence.tests.base import ViewTestCase
from gomobile.convergence.browser import tabs
from gomobile.convergence.behaviors import IMultiChannelBehavior
from gomobile.convergence.interfaces import ContentMediaOption

from zope.schema.interfaces import ConstraintNotSatisfied

class TestBehavior(ViewTestCase):

    def test_has_behavior(self):
        """ Test behavior and assignable works nicely.
        """

        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc

        # Check assignable works
        from plone.behavior.interfaces import IBehaviorAssignable
        assignable = IBehaviorAssignable(doc, None)

        self.assertTrue(assignable.supports(IMultiChannelBehavior))
        self.assertNotEqual(assignable, None)


        # Check behavior works
        self.assertTrue(IMobileContentish.providedBy(doc))
        behavior = IMultiChannelBehavior(doc)

        self.assertNotEquals(behavior, None)

    def test_set_media(self):
        """ Try behavior properties """
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc

        self.assertTrue(IMobileContentish.providedBy(doc))
        behavior = IMultiChannelBehavior(doc)

        self.assertEqual(behavior.contentMedias, ContentMediaOption.USE_PARENT)

        behavior.contentMedias = ContentMediaOption.WEB
        behavior.save()

        # Recreate behavior
        behavior = IMultiChannelBehavior(doc)
        self.assertEqual(behavior.contentMedias, ContentMediaOption.WEB)

    def test_check_registration(self):
        """ Check that our behavior is correctly adapting to IContentish
        """

        from zope.component import getGlobalSiteManager
        sm = getGlobalSiteManager()

        registrations = [a for a in sm.registeredAdapters() if a.provided == IMultiChannelBehavior ]
        self.assertEqual(len(registrations), 1)


    def test_shit_input(self):
        """ Try put in bad data """


        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc
        behavior = IMultiChannelBehavior(doc)
        try:
            behavior.contentMedias = "xxx"
            raise AssertionError("Should not be never reached")
        except ConstraintNotSatisfied:
            pass

    def test_convergence_cataloged(self):
        """ Test that we are compatible with (old) utility class.

        Check that our options also end up to the portal catalog.
        """

        self.setDiscriminateMode("admin")

        self.loginAsPortalOwner()
        from gomobile.convergence.interfaces import ContentMediaOption, IConvergenceMediaFilter, IConvergenceBrowserLayer

        self.filter = getUtility(IConvergenceMediaFilter)

        # Create first a folder structure only for mobile
        sample_folder = self.portal
        sample_folder.invokeFactory("Folder", "mobile_tree", title="Mobile tree")
        self.filter.setContentMedia(sample_folder.mobile_tree, ContentMediaOption.MOBILE)
        sample_folder.mobile_tree.reindexObject()

        # Then create  folder structure for web
        sample_folder.invokeFactory("Folder", "web_tree", title="Web tree")
        self.filter.setContentMedia(sample_folder.web_tree, ContentMediaOption.WEB)
        sample_folder.web_tree.reindexObject()

        # check that our setting is stored correctly
        behavior = IMultiChannelBehavior(sample_folder.mobile_tree)
        self.assertEqual(behavior.contentMedias, ContentMediaOption.MOBILE)

        behavior = IMultiChannelBehavior(sample_folder.web_tree)
        self.assertEqual(behavior.contentMedias, ContentMediaOption.WEB)

        # Check that catalog gives sane results
        catalog = self.getNavtreeData()
        #for i in catalog: print i


        mobile_tree_brain = catalog[-2] # Assume last, as it has been added last
        self.assertEqual(mobile_tree_brain["getContentMedias"], ContentMediaOption.MOBILE)


        web_tree_brain = catalog[-1] # Assume last, as it has been added last
        self.assertEqual(web_tree_brain["getContentMedias"], ContentMediaOption.WEB)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBehavior))
    return suite
