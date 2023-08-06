__license__ = "GPL 2"
__copyright__ = "2009-2012 mFabrik Research Oy"

import logging
from Products.CMFCore.utils import getToolByName
# The profile id of our package:
PROFILE_ID = 'profile-gomobile.convergence:default'


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the importFinalSteps method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('gomobile.convergence')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (('getContentMedias', 'FieldIndex'),
              )
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profile.
    """
    # Only run step if a flag file is present, otherwise this step
    # also gets run when applying a totally unrelated profile.
    if context.readDataFile('gomobile_convergence-default.txt') is None:
        return
    logger = context.getLogger('gomobile.convergence')
    site = context.getSite()
    add_catalog_indexes(site, logger)
