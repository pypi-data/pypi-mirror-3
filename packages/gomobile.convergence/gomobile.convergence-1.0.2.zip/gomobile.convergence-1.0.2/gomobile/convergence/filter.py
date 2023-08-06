"""

    Filtering code responsible for choosing when the item appears on the current media.

    This is the core of convergence: determining what to show and where.

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"

import Missing

import zope.interface
from zope.component import getUtility

from Products import AdvancedQuery

from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, MobileRequestType
from gomobile.convergence.interfaces import IConvergenceSupport, ContentMediaOption, IConvergenceMediaFilter

from gomobile.convergence.behaviors import IMultiChannelBehavior
from gomobile.convergence import PloneMessageFactory as _

media_options_vocabulary = ((ContentMediaOption.USE_PARENT, _(u"Use parent folder settings")),
                                        (ContentMediaOption.WEB, _(u"Web only")),
                                        (ContentMediaOption.MOBILE, _(u"Mobile only")),
                                        (ContentMediaOption.BOTH, _(u"Web and mobile")))


class ConvergedMediaFilter(object):
    """ Helper class to deal with media state of content objects. 
    
    To use this class::
    
        from gomobile.convergence.interfaces import IConvergenceMediaFilter
        self.filter = getUtility(IConvergenceMediaFilter)
        
        
    .. note ::
    
        This class is mostly deprecated and will be removed in the future.
        Please use IMultiChannelBehavior directly.
        
    
    """
    
    zope.interface.implements(IConvergenceMediaFilter)
    
    def isConvergedContent(self, content):
        """ See that the content is proper converged supported """

        if not IConvergenceSupport.providedBy(content):
            return False

        try:
            behavior = IMultiChannelBehavior(content)
        except TypeError:
            return False

        return behavior != None

    def getContentMedia(self, content):
        """ Return content media value for queried content.

        If value is "parent" query parent object.
        """

        try:
            behavior = IMultiChannelBehavior(content)
        except TypeError:
            return False

        if behavior == None:
            return ContentMediaOption.USE_PARENT

        return behavior.contentMedias

    def setContentMedia(self, content, strategy):
        """ Set content option on which medias the content should be visible.

        This method is permission aware.

        @param content: AT based object whose schema is patched by extender

        @param strategy: one of strings web, mobile, parent, both
        """

        try:
            behavior = IMultiChannelBehavior(content)
        except TypeError:
            raise RuntimeError("Content does not support multi channel behavior")

        if behavior == None:
            raise RuntimeError("Content does not support multi channel behavior")

        behavior.contentMedias = strategy
        
        # Make change persistent
        behavior.save()


    def solveContentMedia(self, content):
        """ Acquire media platforms value for the particular content object.

        Walk thorugh parent object chain until we have found meaningful value are we mobile or not.
        """

        # TODO: We don't trust Zope acquisition,
        # walk tree upwards until we have a value
        while content != None:

            if not IConvergenceSupport.providedBy(content):
                break

            val = self.getContentMedia(content)
            if val != ContentMediaOption.USE_PARENT:
                return val

            content = content.aq_parent

        # Not defined, return both
        return ContentMediaOption.BOTH


    def checkMediaFilter(self, obj_media, medias):
        """ Check whether object should be displayed

        @param obj_media: Resolved object's medias
        @param medias: What medias we are showing, of of ContentMediaOption.BOTH,ContentMediaOption.MOBILE or ContentMediaOption.WEB
        @return True if obj should be displayed
        """

        # We need to resolve parent checking elsewhere
        assert medias != ContentMediaOption.USE_PARENT

        if medias == ContentMediaOption.BOTH:
            return True

        value = obj_media

        if value == None:
            raise RuntimeError("Should not happen")

        if value == ContentMediaOption.BOTH:
            return True
        else:
            # web=web or mobile=mobile
            return value == medias

    def filterObject(self, obj, medias):
        """ Check whether the object should be rendered in the targeted medias.

        @param medias: IConvergenceSupport.CONTENT_MEDIA_OPTION constant, excluding parent

        @return: True if the content should appear on the media
        """

        if medias == ContentMediaOption.BOTH:
            return True

        value = self.solveContentMedia(obj)

        return self.checkMediaFilter(value, medias)


    def retrofitNavTree(self, tree):
        """ Cram media availability info into sitemap.

        Adds content_media key to each Navtree leaf.
        Calculate content_media inheritance.
        """

        def walk(parent_media, node):
            """ Recurse through navtree and patch in media """

            # Check whether we have already resolved content media
            # for this node (should not actually happen)
            if not "content_media" in node:

                # This item overrides the content media setting
                overridden_media = node.get("getContentMedias", None)

                #data = node.copy()
                #if "children" in data:
                #    del data["children"]

                #if "getURL" in node:
                #    print node["getURL"] + "->" + str(overridden_media)

                if overridden_media and overridden_media != "parent":
                    my_media = overridden_media
                else:
                    my_media = parent_media



                node["content_media"] = my_media

            for child in node["children"]:
                walk(my_media, child)

        # TODO: If the tree doesn't start from the portal root we are screwed up

        walk(ContentMediaOption.BOTH, tree)



    def filterNavTree(self, tree, target_medias):
        """ Remove non-appropriate medias from the navigation tree.
        """

        def walk(node):
            """ Recurse through navtree and patch in media """

            bad_childs = []

            for child in node["children"]:

                media = child["content_media"]

                #if "getURL" in child:
                #    print "Checking " + child["getURL"] + " against " + media + " " + target_medias

                if not self.checkMediaFilter(media, target_medias):
                    # Cannot remove nodes whilst in iterator
                    bad_childs.append(child)
                else:
                    walk(child)

            for child in bad_childs:
                node["children"].remove(child)

        # TODO: If the tree doesn't start from the portal root we are screwed up

        walk(tree)

    def getContentMediaStrategy(self, context, request):
        """ Return what content we should include.

        1. If we are in web and logged in, include all - admin must see the content he/she edits

        2. If we are in web and not logged in, include web only

        3. If we are in mobile, include mobile only

        @param request: HTTPRequest object or None if not available
        """

        if request == None:
            # Default to web
            return ContentMediaOption.WEB

        discriminator = getUtility(IMobileRequestDiscriminator)
        request_types = discriminator.discriminate(context, request)

        if MobileRequestType.ADMIN in request_types:
            return ContentMediaOption.BOTH

        if MobileRequestType.WEB in request_types:
            return ContentMediaOption.WEB

        if MobileRequestType.MOBILE in request_types:
            return ContentMediaOption.MOBILE

        raise RuntimeError("Should not happen:" + str(context) + " " + str(request_types))


    def solveCatalogBrainContenMedia(self, context, brains):
        """ Get content media states for arbitary portal_catalog searches.

        We need to perform additional query to resolve all content media states in the tree.

        To solve the content media state, we need to know the full parent chain of the object.
        Querying this can be expensive. Try be smart here.

        @param brains: Iteration of ZCatalog mybrains objects

        @return: look up dictionary brain -> content media state
        """

        # Pats we need to query to solve all parents of the brains
        paths = []

        # Brain -> content media type mappings
        result = {}

        # Brain -> path cache.
        # Each brain.getPath() takes considerable time due acquisition call and kills performance
        # we cache results here
        brain_paths = {}

        def getBrainPath(brain):
            """ Cached item path look up """
            if not brain in brain_paths:
                brain_paths[brain] = brain.getPath()

            return brain_paths[brain]

        # Build a list of containing all paths and their parent paths
        # we need to have in order to resolve content media inheritance
        for b in brains:
            path = getBrainPath(b)

            parts = path.split("/")
            parts = parts[:-1] # Strip the last path part away, effectively getting parent path

            parents = []
            for p in parts:
                parents.append(p)
                parent_path = "/".join(parts)

                # Because there might be intersections,
                # we need to check that parent has not been previously added
                if not parent_path in paths:
                    # We cannot query the portal itself - causes exception
                    paths.append(parent_path)

        # Build
        def getPathQuery(p):
            """ ExtendedPathIndex catalog query options to receive brain for this path """
            return AdvancedQuery.Generic("path", {"query" : p, "depth" : 0 })

        queries = [ getPathQuery(p) for p in paths ]

        # TODO: The following query might be too expensive...
        # Do catalog search which matches any of our paths
        if len(paths) > 0:
            all_parent_brains = context.portal_catalog.evalAdvancedQuery(AdvancedQuery.Or(*queries))
            all_brains = all_parent_brains + brains
        else:
            # Nothing to query (we have only root level content)
            all_brains = brains


        def getBrainParentPath(brain):
            parts = getBrainPath(brain).split("/")
            parts = parts[:-1]
            return "/".join(parts)

        def findBrain(path):
            """ Get a previously queried brain based on its path """
            for b in all_brains:
                if getBrainPath(b) == path:
                    return b

            # Check if this is the portal itself
            #raise RuntimeError("No brain for path:" + path)

            return None


        # Now walk through the brains and calculate parent path info
        def walk(brain):

            # We might not have content media value set for this item (does not support convergence)
            # or it might have set to use parent value
            if brain["getContentMedias"] == Missing.Value or brain["getContentMedias"] == ContentMediaOption.USE_PARENT:
                # Inherit media setting
                parent_path = getBrainParentPath(brain)
                parent = findBrain(parent_path)

                if parent is None:
                    # Assume the path is portal itself
                    # and we hit the roof of parent chain
                    result[brain] = ContentMediaOption.BOTH
                else:
                    if parent not in result:
                        walk(parent)
                    result[brain] = result[parent]
            else:
                # Media setting overridden
                result[brain] = brain["getContentMedias"]


        # This will use recurse + result caching to resolve
        # content media setting for every brain in nav tree hierarchy
        for b in all_brains:
            walk(b)

        #for r in result.items():
        #    print str(r)

        return result


def getConvergenceMediaFilter():
    """
    Helper method to make sure things work.
    """
    
    # Workaround for getUtility() bug 
    # getUtility() works not, getUtilitiesFor() works
    from zope.component import getGlobalSiteManager
    gsm = getGlobalSiteManager()
    return gsm.getUtility(IConvergenceMediaFilter)

  