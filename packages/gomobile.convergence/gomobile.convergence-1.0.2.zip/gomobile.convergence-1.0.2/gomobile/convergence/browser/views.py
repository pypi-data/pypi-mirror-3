"""

    Views for accessing and editing convergence options.

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

from AccessControl import Unauthorized

from zope.interface import implements, Interface
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.app.component.hooks import getSite
from zope.component import getUtility, queryUtility

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from five import grok
from zope.component import queryAdapter, getUtility

from Products.Five import BrowserView
from five import grok
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFCore.interfaces import IContentish

from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, IMobileSiteLocationManager, MobileRequestType
from gomobile.mobile.interfaces import IMobileRedirector

from gomobile.convergence.interfaces import ContentMediaOption, IConvergenceMediaFilter
from gomobile.convergence.interfaces import IOverrider
from gomobile.convergence.interfaces import IConvergenceSupport, ContentMediaOption

from gomobile.convergence.filter import getConvergenceMediaFilter

class ChangeMediaStrategyView(BrowserView):
    """
    Handle change media strategy portlet form posts.
    """

    def __call__(self):

        strategy = self.request["media_option"]

        # We reallly want to edit folder settings,
        # this magic this juts work (tm)
        self.context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        isDefaultPage = self.context_state.is_default_page()

        if isDefaultPage:
            # Use parent folder, no point of changing the
            # folder front page setting
            instance = self.context.aq_inner.aq_parent
        else:
            instance = self.context

        filter = getConvergenceMediaFilter()

        filter.setContentMedia(instance, strategy)


        # Update portal_catalog to reflect new changes
        #self.context.reindexObject(idxs=["getContentMedias"])

        # Go back to the object front page
        self.request.response.redirect(self.context.absolute_url())



class OverriderView(BrowserView):
    """  Helper views to allow easy access to overridden data from templates.

    Enable converged proxy object if we are in mobile mode.

    How to traverse to find mobile overrides and redefine context in safe way::

        context context/@@multichannel_overrider|nocall:context; here nocall:context;

    This will give you context unmodified if convergence is not installed.
    """

    def __call__(self):
        """
        """

        util = getUtility(IMobileRequestDiscriminator)
        flags = util.discriminate(self.context, self.request)

        if MobileRequestType.MOBILE in flags:

            overrider = queryAdapter(self.context, IOverrider)
            if overrider is not None:
                return overrider

        # No overrides, use context as is
        return self.context
    
        
class AbstractGoToView(BrowserView):
    """ Helper view to redirect user to the mobile site.
    
    This is mostly useful when used as a helper view from site_actions.
    """
    
    def get_available_medias(self):
        """
        @return: Tuple of ids where the target media must be available to make this link active.
        """
        raise NotImplementedError("Abstract method")
    
    def get_target_media(self):
        """
        @return: "www" or "mobile"
        """
        raise NotImplementedError("Abstract method")    
    
    def is_available(self, context):
        """
        @return: True if the queried is available as a mobile version.
        """
        filter = queryUtility(IConvergenceMediaFilter, None)
        if filter is None:
            # convergence is not quickinstalled, assume always available
            return True
            
        media = filter.solveContentMedia(context)
        return media in self.get_available_medias()
        
    def __call__(self):
        """ Try to go the current content on the mobile site, otherwise go to the homepage.
        
        @return: Nothing but modifies HTTP response to be a redirect
        """
        context = self.context.aq_inner
        if self.is_available(context):
            redirect_context = context
        else:
            portal = context.portal_url.getPortalObject()
            redirect_context = portal
        
        query_string = self.request["QUERY_STRING"]    
        
        redirector = getMultiAdapter((redirect_context, self.request), IMobileRedirector)
        
        return redirector.redirect_url(redirect_context.absolute_url(), query_string, media_type=self.get_target_media())
    
class GoToMobileSiteView(AbstractGoToView):
    """    
    Use ${context/absolute_url}/@@go_to_mobile_site view to redirect visitors manually to mobile version of the site.    
    """
    def get_available_medias(self):
        return (ContentMediaOption.BOTH, ContentMediaOption.MOBILE)
    
    def get_target_media(self):
        return "mobile"
    
class GoToWebSiteView(AbstractGoToView):
    """
    Use ${context/absolute_url}/@@go_to_web_site view to redirect visitors manually to web version of the site.
    """
    
    def get_available_medias(self):
        return (ContentMediaOption.BOTH, ContentMediaOption.WEB)
    
    def get_target_media(self):
        return "web"
            