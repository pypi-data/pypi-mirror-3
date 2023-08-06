"""
    Include content media information in portal_catalog indexing and search output.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__docformat__ = "epytext"

from zope.component import getUtility, queryUtility

import Missing

from interfaces import IConvergenceSupport, IConvergenceMediaFilter

from gomobile.convergence.behaviors import IMultiChannelBehavior


def _getContentMedias(object, portal, **kw):
    """ New and old indexer core """

    try:
        behavior = IMultiChannelBehavior(object)
    except TypeError:
        # OBject is not type which supports behavior adaptions
        return Missing.Value

    if behavior == None:
        # Multichannel behavior has been disabled for the object by
        # behavior assignable
        return Missing.Value

    medias = behavior.contentMedias

    return medias


# Plone 3.3.x way
try:
    from plone.indexer.decorator import indexer

    @indexer(IConvergenceSupport)
    def getContentMedias(object, **kw):
        """ Provide indexing hook for portal_catalog for all converged content.

        Store multi channel medias for later nav tree generating.
        """
        return _getContentMedias(object, None, **kw)


except ImportError:
    # Plone 3.2.x code

    from Products.CMFPlone.CatalogTool import registerIndexableAttribute

    def getContentMedias(object, portal, **kw):
        """ Provide indexing hooksk for portal_catalog """
        return _getContentMedias(object, portal, **kw)


    registerIndexableAttribute('getContentMedias', getContentMedias)
