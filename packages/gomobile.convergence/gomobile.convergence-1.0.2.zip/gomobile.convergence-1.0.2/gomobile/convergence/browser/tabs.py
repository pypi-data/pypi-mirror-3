"""

    Patch site section tabs to discriminate between web and mobile content.

"""

__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility, queryUtility

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.Five import BrowserView

from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.browser.interfaces import INavigationTree
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder, SitemapQueryBuilder

from plone.app.layout.navigation.interfaces import INavtreeStrategy

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

from Products.CMFPlone.browser import navigation
from zope.component import getMultiAdapter, queryMultiAdapter

from gomobile.convergence.interfaces import IConvergenceMediaFilter

from Products.CMFPlone.browser.navigation import get_view_url

try: 
    # Plone 4 and higher 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3

class CatalogNavigationTabs(navigation.CatalogNavigationTabs):
    """ Filter site tabs for web, mobile and admin.
    
    This is copy-paste + 5 lines patch from Plone 3.2.1 code.
    """

    def topLevelTabs(self, actions=None, category='portal_tabs'):
        
        context = aq_inner(self.context)

        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')

        # Build result dict
        result = []
        
        if PLONE_VERSION == 3:
            # BBB to Plone 3, different actions input signature
            # http://svn.plone.org/svn/plone/Plone/tags/3.3.5/Products/CMFPlone/browser/navigation.py
            # first the actions
            if actions is not None:
                for actionInfo in actions.get(category, []):
                    data = actionInfo.copy()
                    data['name'] = data['title']
                    result.append(data)            
        else:
        
            if actions is None:
                context_state = getMultiAdapter((context, self.request),
                                                name=u'plone_context_state')
                actions = context_state.actions(category)

            # first the actions
            if actions is not None:
                for actionInfo in actions:
                    data = actionInfo.copy()
                    data['name'] = data['title']
                    result.append(data)

        # check whether we only want actions
        if site_properties.getProperty('disable_folder_sections', False):
            return result

        customQuery = getattr(context, 'getCustomNavQuery', False)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        rootPath = getNavigationRoot(context)
        query['path'] = {'query' : rootPath, 'depth' : 1}

        query['portal_type'] = utils.typesToList(context)
        
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute

            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', [])

        query['is_default_page'] = False
        
        if site_properties.getProperty('disable_nonfolderish_sections', False):
            query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        idsNotToList = navtree_properties.getProperty('idsNotToList', ())
        excludedIds = {}
        for id in idsNotToList:
            excludedIds[id]=1

        rawresult = portal_catalog.searchResults(**query)
                
        # apply mobile media filter for the results
        media_filter = queryUtility(IConvergenceMediaFilter, None)
        
        if media_filter is not None:
            strategy = media_filter.getContentMediaStrategy(self.context, self.request)        
            resolved_content_medias = media_filter.solveCatalogBrainContenMedia(self.context, rawresult)
        
        #import pdb ; pdb.set_trace()
        # now add the content to results
        for item in rawresult:
            
            if not (excludedIds.has_key(item.getId) or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                data = {'name'      : utils.pretty_title_or_id(context, item),
                        'id'         : item.getId,
                        'url'        : item_url,
                        'description': item.Description}
        
                if media_filter is not None:
                    # Behavior with gomobile.convergence
                    media = resolved_content_medias[item]
                    if media_filter.checkMediaFilter(media, strategy):
                        result.append(data)
                else:
                    # The default behavior
                    result.append(data)                    
                                
        return result
