__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


# Various base classes and modules
from zope.component import getUtility, queryUtility
from plone.app.layout.navigation import navtree as navtree_base
from Products.CMFPlone.browser import navtree as cmfplone_navtree
from Products.CMFCore import PortalFolder

from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, MobileRequestType
from gomobile.convergence.interfaces import IConvergenceSupport, ContentMediaOption, IConvergenceMediaFilter


from zope.interface import implements
from zope.component import getMultiAdapter, queryUtility

class ConvergedNavtreeStrategy(cmfplone_navtree.DefaultNavtreeStrategy):
    """ We don't change this, but actually play with buildForNavtree function """    
    pass


# MONKEY-PATCH TIME!
# Triggered by __init__.py


# Fix sitemap/navigation portlet generation
old_buildFolderTree = navtree_base.buildFolderTree


def mobileAware_buildFolderTree(context, obj=None, query={}, strategy=navtree_base.NavtreeStrategyBase()):
    """ Monkey patch Plone's generic navigation tree builder
    """
    
    
    filter = queryUtility(IConvergenceMediaFilter, None)

    
    # First query nav tree using default plone strategy
    items = old_buildFolderTree(context, obj, query, strategy)
    
    if filter is None:
        # gomobile.convergence is not installed
        return items
            
    # Then put in converged media info
    filter.retrofitNavTree(items)
            
    # Then filter out items which are not propriate in the current request context
    medias = filter.getContentMediaStrategy(context, context.REQUEST)
    
    filter.filterNavTree(items, medias)
    
    return items

navtree_base.buildFolderTree = mobileAware_buildFolderTree

def mobile_contentItems(self, filter=None):
    """ Monkey patch Plone's folder listing.
    """
    # List contentish and folderish sub-objects and their IDs.
    # (method is without docstring to disable publishing)
    #    
    ids = self.objectIds()
    filtered = self._filteredItems(ids, filter)
    
    
    filter = queryUtility(IConvergenceMediaFilter, None)
    if filter is None:
        # gomobile.convergence is not installed
        return filtered
        
        
    # May not be available
    # - uni tests
    # - command line client
    request = getattr(self, "REQUEST", None)
        
    medias = filter.getContentMediaStrategy(self, request)
    
    filtered = [ (id, obj) for id, obj in filtered if filter.filterObject(obj,medias) ]
    return filtered

# Make PortalFolderBase mobile aware by monkey patching folder listing
PortalFolder.PortalFolderBase.contentItems = mobile_contentItems


# We could override this with components but this goes for now

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility, queryUtility

old_decoratorFactory = cmfplone_navtree.SitemapNavtreeStrategy.decoratorFactory

def decoratorFactory(self, node):
    """ Monkey patch Plone's navigation tree information to include content media
    """

    context = aq_inner(self.context)
    request = context.REQUEST    
    
    newNode = node.copy()
    item = node['item']

    portalType = getattr(item, 'portal_type', None)
    itemUrl = item.getURL()
    if portalType is not None and portalType in self.viewActionTypes:
        itemUrl += '/view'

    isFolderish = getattr(item, 'is_folderish', None)
    showChildren = False
    if isFolderish and (portalType is None or portalType not in self.parentTypesNQ):
        showChildren = True

    ploneview = getMultiAdapter((context, request), name=u'plone')

    newNode['Title'] = utils.pretty_title_or_id(context, item)
    newNode['id'] = item.getId
    newNode['absolute_url'] = itemUrl
    newNode['getURL'] = itemUrl
    newNode['path'] = item.getPath()
    newNode['icon'] = getattr(item, 'getIcon', None) # Deprecated, use item_icon
    newNode['item_icon'] = ploneview.getIcon(item)
    newNode['Creator'] = getattr(item, 'Creator', None)
    newNode['creation_date'] = getattr(item, 'CreationDate', None)
    newNode['portal_type'] = portalType
    newNode['review_state'] = getattr(item, 'review_state', None)
    newNode['Description'] = getattr(item, 'Description', None)
    newNode['getRemoteUrl'] = getattr(item, 'getRemoteUrl', None)
    newNode['show_children'] = showChildren
    newNode['no_display'] = False # We sort this out with the nodeFilter
    newNode['link_remote'] = newNode['getRemoteUrl'] and newNode['Creator'] != self.memberId

    idnormalizer = queryUtility(IIDNormalizer)
    newNode['normalized_portal_type'] = idnormalizer.normalize(portalType)
    newNode['normalized_review_state'] = idnormalizer.normalize(newNode['review_state'])
    newNode['normalized_id'] = idnormalizer.normalize(newNode['id'])

    newNode['getContentMedias'] = getattr(item, 'getContentMedias', None)
    newNode['Language'] = getattr(item, 'Language', "neutral language")
    
    return newNode

cmfplone_navtree.SitemapNavtreeStrategy.decoratorFactory = decoratorFactory
