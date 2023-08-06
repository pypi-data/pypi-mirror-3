"""

    Test override objects.

"""

__license__ = "GPL 2"
__copyright__ = "2009-2011 mFabrik Research Oy"

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.convergence.interfaces import IOverrider
from gomobile.convergence.overrider.base import IOverrideStorage

from base import BaseTestCase, FunctionalTestCase

# TODO: This depends on z3c.form version?
SAVE_OK = "Data successfully updated"

class TestMobileOverrides(BaseTestCase):

    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")

    def create_event(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Event", "event")

    def test_get_field_list(self):
        """
        Test that we populate enabled fields vocabulary correctly from override schema.
        """

        from gomobile.convergence.overrider.base import get_field_list
        from gomobile.convergence.overrider.document import DocumentOverrideStorage
        storage = DocumentOverrideStorage()

        fields = get_field_list(storage)
        assert "Title" in fields.by_token

    def test_has_overrides(self):
        """ Document object overrides are enabled by default
        """
        self.create_doc()
        doc = self.portal.doc
        overrider = IOverrider(doc)
        assert overrider != None

        assert overrider.schema != None
        self.assertEqual(overrider._getOverrideFieldNames(), ["Title", "Description", "getText"])

        # Set one override enabled and check it is read properly
        storage = IOverrideStorage(doc)

        storage.enabled_overrides = ["Title"]
        self.assertEqual(overrider._isOverrideEnabled("Title", storage), True)
        self.assertEqual(overrider._isOverrideEnabled("Description", storage), False)

        # Set overriden title
        storage.Title = u"Foobar"

        # Call title accessor by emulator IOverrider steps
        # and see each microstep completes
        self.assertTrue(overrider._isOverride("Title"))
        storage = IOverrideStorage(self.portal.doc)
        self.assertTrue(overrider._isOverrideEnabled("Title", storage))
        self.assertEqual(overrider._getOverrideOrOrignal("Title")(), u"Foobar")

        assert overrider.Title() == u"Foobar"

    def test_has_no_overrides(self):
        """ Event object does not have default overrides
        """
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Event", "event")
        event = self.portal.event

        try:
            overrider = IOverrider(event)
            raise AssertionError("Should not be never reached")
        except TypeError:
            pass

    def test_traverse_checker(self):
        """ Check that condition view works """
        self.create_doc()
        self.create_event()


        result = self.portal.doc.restrictedTraverse("@@supports_mobile_overrides")
        result = result()
        self.assertEqual(result, True)


        result = self.portal.event.restrictedTraverse("@@supports_mobile_overrides")
        result = result()
        self.assertEqual(result, False)

    def test_render_form(self):
        self.create_doc()

        result = self.portal.doc.restrictedTraverse("@@edit_mobile_overrides")
        result()

    def test_convergence_form(self):
        self.create_doc()

        result = self.portal.doc.restrictedTraverse("@@convergence")

        self.assertEqual(result.media_status(), u"Web and mobile")

        # Test rendeing HTML without errors
        result()


class TestMobileOverridesFunctional(FunctionalTestCase):
    """ Functional tests for mobile overrides settings page. """

    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        return self.portal.doc
    
    def test_set_mobile_title_override(self):
        """
        Check that mobile folder listing page setting can be toggled properly.
        """
        
        doc = self.create_doc()
        
        self.loginAsAdmin()
        
        self.browser.open(doc.absolute_url() + "/@@convergence")
        #self.assertNotDefaultPloneTheme(self.browser.contents)
        #self.browser.open(self.portal.doc.absolute_url())
        html = self.browser.contents
        
        # Assume we have good settings page
        self.assertTrue("form-widgets-Title" in html, "Was not a convergence settings pages")
        
        form = self.browser.getForm(name="convergence")        
        form.getControl(name=u"form.widgets.enabled_overrides:list").value = [u"Title"]
        form.getControl(name=u"form.widgets.Title").value = u"Overriden title text"
        save = form.getControl(name=u"form.buttons.save")
        save.click()
    
        # back to View mode    
        html = self.browser.contents
        self.assertTrue(SAVE_OK in html)
        
        # Go to back to settings and see the setting has been saved
        self.browser.open(doc.absolute_url() + "/@@convergence")
        form = self.browser.getForm(name="convergence")
        value = form.getControl(name=u"form.widgets.enabled_overrides:list").value 
        self.assertEqual(value, [u"Title"], "Title override setting properly stored")
        value = form.getControl(name=u"form.widgets.Title").value
        self.assertEqual(value, u"Overriden title text")
        
        # Now ensure title has been changed in mobile rendering
        self.useMobileMode()
        self.browser.open(doc.absolute_url())
        html = self.browser.contents
        self.assertTrue("Overriden title text" in html)


    def test_set_appear_in_mobile_folder_listing_setting(self):
        """ 
        Check that this setting is correctly set and effective.
        """
        
        doc = self.create_doc()
        
        self.loginAsAdmin()
        
        # Set the setting
        self.browser.open(doc.absolute_url() + "/@@convergence")        
        form = self.browser.getForm(name="convergence")        
        form.getControl(name=u"mobile.widgets.mobileFolderListing:list").value = [u"true"]
        save = form.getControl(name=u"form.buttons.save")
        save.click()
        
        # Assume we get the happy response
        # back to View mode    
        html = self.browser.contents
        self.assertTrue(SAVE_OK in html)  

        # Then reload the page to see if the change was persistent
        self.browser.open(doc.absolute_url() + "/@@convergence")        
        form = self.browser.getForm(name="convergence")        
        value = form.getControl(name=u"mobile.widgets.mobileFolderListing:list").value
        
        if value[0] not in [u"true", "selected"]:
            # TODO: selected = new z3c.form? Used to be true.
            raise AssetionError("Setting was not properly perisistent:" + str(value))
        
        # Then check if the folder list still appears
        self.loginAsPortalOwner()




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMobileOverrides))
    suite.addTest(unittest.makeSuite(TestMobileOverridesFunctional))
    return suite



