"""

    Test multi-channel behavior object.

"""

__license__ = "GPL 2"
__copyright__ = "2010-2011 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = "epytext" 

import unittest

from zope.component import getMultiAdapter, getUtility

from gomobile.mobile.interfaces import IMobileContentish

from gomobile.convergence.tests.base import BaseTestCase
from gomobile.convergence.behaviors import IMultiChannelBehavior
from gomobile.convergence.interfaces import ContentMediaOption


from zope.annotation.interfaces import IAnnotations

class TestUninstall(BaseTestCase):

    def make_some_evil_site_content(self):
        """ Test behavior and assignable works nicely.
        """

        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc
        doc.processForm()

        # Check assignable works
        from plone.behavior.interfaces import IBehaviorAssignable
        assignable = IBehaviorAssignable(doc, None)

        self.assertTrue(assignable.supports(IMultiChannelBehavior))
        self.assertNotEqual(assignable, None)


        # Check behavior works
        self.assertTrue(IMobileContentish.providedBy(doc))
        behavior = IMultiChannelBehavior(doc)
        behavior.contentMedias = ContentMediaOption.BOTH
        behavior.save()

    def uninstallRun(self, name="gomobile.convergence"):
        qi = self.portal.portal_quickinstaller
        
        try:
            qi.uninstallProducts([name])
        except:
            pass
        #qi.installProduct(name)        
    
    def test_annotations(self):
        """ Check that uninstaller cleans up annotations from the docs
        """
        self.make_some_evil_site_content()

        annotations = IAnnotations(self.portal.doc)
        self.assertTrue("multichannel" in annotations)
        
        self.uninstallRun()
        
        annotations = IAnnotations(self.portal.doc)
        self.assertFalse("multichannel" in annotations)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUninstall))
    return suite
