"""

    Convergence test base classes
    
    http://webandmobile.mfabrik.com

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"

from Products.Five import zcml
from Products.Five import fiveconfigure
from zope.component import getUtility, queryUtility
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.interface import directlyProvidedBy, directlyProvides

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from gomobile.mobile.tests import utils
from gomobile.convergence.interfaces import ContentMediaOption, IConvergenceMediaFilter, IConvergenceBrowserLayer


@onsetup
def setup_zcml():

    fiveconfigure.debug_mode = True
    import gomobile.convergence
    zcml.load_config('configure.zcml', gomobile.convergence)
    zcml.load_string(utils.ZCML_INSTALL_TEST_DISCRIMINATOR)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('gomobile.mobile')
    ztc.installPackage('gomobile.convergence')
    ztc.installPackage('gomobiletheme.basic')


# The order here is important.
setup_zcml()
#extension_profiles=['Products.CMFPlone:testfixture']
ptc.setupPloneSite(products=['gomobile.mobile', 'gomobile.convergence', 'plone.app.z3cform', 'gomobiletheme.basic'],extension_profiles=['Products.CMFPlone:testfixture'])

class ConvergenceTestCaseMixin:

    def afterSetUp(self):

        # A hack to force gomobile.convergence install when running multiple tests on P3
        name = "gomobile.convergence"
        qi = self.portal.portal_quickinstaller
        
        try:
            qi.uninstallProducts([name])
        except:
            pass
        qi.installProduct(name)        
        
        self.filter = getUtility(IConvergenceMediaFilter)

        # Set up convergence layer on HTTP request,
        # so that configure overrides kick in


        from plone.browserlayer import utils

        # TODO: Put following into a test case
        self.assertTrue(IConvergenceBrowserLayer in utils.registered_layers())

        # Make sure that convergence layer is applied on the test request,
        # so that our custom views kick in
        #import pdb ; pdb.set_trace()
        directlyProvides(self.portal.REQUEST, [IConvergenceBrowserLayer] + list(directlyProvidedBy(self.portal.REQUEST)))


    def setDiscriminateMode(self, mode):
        """
        Spoof the following HTTP request media.

        @param: "mobile", "web" or other MobileRequestType pseudo-constant
        """
        from gomobile.mobile.tests.utils import TestMobileRequestDiscriminator
        TestMobileRequestDiscriminator.setModes([mode])

        # skin manager must update active skin for the request
        self._refreshSkinData()


    def flatten(self, tree):
        """ Turn navigation tree into 1-dimesional array """
        array = []

        def flatten(node):
            """ Flatten navigation tree to one dim. array for easier testing """
            for item in node['children']:
                array.append(item)
                flatten(item)

            return array

        return flatten(tree)

    def getEntryByPath(self, flat, path):
        """ Search navigation tree entry by its path """
        url = self.portal.absolute_url() + path

        for i in flat:
            if i["getURL"] == url:
                return i

        raise KeyError("No item:" + path)

    def getNavtreeData(self):
        """ Create navigation tree data for the site """
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='sitemap_builder_view')

        data = view.siteMap()

        data = self.flatten(data)
        return data

    def create_sample_structure(self):
        """ Set up sample content structure for testing """
        self.loginAsPortalOwner()

        #self.portal.invokeFactory("Folder", "folder")
        sample_folder = self.portal
        #self.portal.portal_workflow.doActionFor(sample_folder, "publish")
        #self.portal.reindexObject()

        sample_folder.invokeFactory("Folder", "mobile_tree", title="Mobile tree")
        sample_folder.mobile_tree.invokeFactory("Document", "mobile_tree_inside_1")
        sample_folder.mobile_tree.invokeFactory("Document", "mobile_tree_inside_2")
        sample_folder.invokeFactory("Folder", "web_tree", title="Web tree")
        sample_folder.web_tree.invokeFactory("Folder", "web_tree_inside_1")
        sample_folder.invokeFactory("Document", "web_doc")
        sample_folder.invokeFactory("Document", "mobile_doc")
        sample_folder.invokeFactory("Folder", "generic_tree", title="Generic tree")
        sample_folder.generic_tree.invokeFactory("Document", "generic_tree_inside_1")

        self.filter.setContentMedia(sample_folder.mobile_tree, ContentMediaOption.MOBILE)
        self.filter.setContentMedia(sample_folder.mobile_doc, ContentMediaOption.MOBILE)
        self.filter.setContentMedia(sample_folder.web_tree, ContentMediaOption.WEB)
        web = self.filter.getContentMedia(sample_folder.web_tree)

        self.filter.setContentMedia(sample_folder.web_doc, ContentMediaOption.WEB)
        self.filter.setContentMedia(sample_folder.generic_tree, ContentMediaOption.BOTH)

        # TODO: Had problems with cataloging in unit tests
        # not sure if the following helped
        import transaction
        transaction.get().savepoint()

        for tree in [ sample_folder, sample_folder.generic_tree, sample_folder.mobile_tree, sample_folder.web_tree ]:
            tree.reindexObject(idxs=["getContentMedias"])
            for id,obj in tree.contentItems():
                self.portal.portal_workflow.doActionFor(obj, "publish")
                obj.reindexObject(idxs=["getContentMedias"])

        self.logout()

        return sample_folder


class BaseTestCase(ConvergenceTestCaseMixin, ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
class ViewTestCase(ConvergenceTestCaseMixin, PloneTestCase):
    """ We need different inherintance for this test case or stock views are not set up properly """

    def afterSetUp(self):
        PloneTestCase.afterSetUp(self)
        ConvergenceTestCaseMixin.afterSetUp(self)

from gomobiletheme.basic.tests import BaseTestCase as FunctionalBaseTestCase
class FunctionalTestCase(ConvergenceTestCaseMixin, FunctionalBaseTestCase):

    def afterSetUp(self):
        FunctionalBaseTestCase.afterSetUp(self)
        ConvergenceTestCaseMixin.afterSetUp(self)
