__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

from zope.interface import implements
from zope.component import getUtility
from zope import schema
from zope.interface import implements, Interface
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.app.component.hooks import getSite


from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider

from zope.component import getUtility, queryUtility
from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType
from gomobile.convergence.interfaces import IConvergenceMediaFilter

from gomobile.convergence.filter import media_options_vocabulary
from gomobile.convergence import PloneMessageFactory as _

from gomobile.convergence.filter import getConvergenceMediaFilter

class IMediaPortlet(IPortletDataProvider):
    """ Define buttons for mobile preview """
    pass

class Renderer(base.Renderer):
    """ Draw content media options portlet """

    index = ViewPageTemplateFile('media.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.site_url = getToolByName(context, 'portal_url')
        self.filter = getConvergenceMediaFilter()
        self.discriminator = getUtility(IMobileRequestDiscriminator)
        self.context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')

        isDefaultPage = self.context_state.is_default_page()

        if isDefaultPage:
            # Use parent folder, no point of changing the
            # folder front page setting
            self.actual_context = self.context.aq_inner.aq_parent
        else:
            self.actual_context = self.context

    def media_options(self):
        return media_options_vocabulary

    def current_media(self):
        media = self.filter.solveContentMedia(self.context)
        # Translate
        for id, text in media_options_vocabulary:
            if id == media:
                return text

    def is_media_checked(self, media):
        return self.filter.getContentMedia(self.context) == media and "CHECKED" or None

    def is_visible(self):
        flags = self.discriminator.discriminate(self.context, self.request)
        admin = MobileRequestType.ADMIN in flags
        converged = self.filter.isConvergedContent(self.actual_context)
        return admin and converged

    def render(self):
        if self.is_visible():
          return self.index()
        else:
          return ""

class Assignment(base.Assignment):
    """ Assigner for grey static portlet. """
    implements(IMediaPortlet)

    title = _(u"Content medias")


class AddForm(base.NullAddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    def create(self):
        return Assignment()
