"""

     Misc. helper functions

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

import copy

import zope.schema
from zope.schema.vocabulary import SimpleTerm

def make_terms(items):
    """ Create zope.schema terms objects based on tuples of (value, Title) """
    terms = [ c(value=pair[0], token=pair[0], title=pair[1]) for pair in items ]
    return terms



def addSchema(target, source):
    """ Combine zope.schema fields from another class.

    The function will retain the order of the fields.
    New fields will be appended last.

    @param source: Class having zope.schema fields

    @param target: any Class with or without zope.schema fields
    """

    # Schema retains declaration order
    order = 0

    # zope.schema uses order to know the order
    # of declaration... start from the last field
    fields = zope.schema.getFieldsInOrder(target)
    if len(fields) > 0:
        order = max([ f.order for f in fields])

    for name, field in zope.schema.getFieldsInOrder(source):
        dupe = copy.copy(field)
        dupe.order = order
        setattr(target, name, dupe)
        order += 1


