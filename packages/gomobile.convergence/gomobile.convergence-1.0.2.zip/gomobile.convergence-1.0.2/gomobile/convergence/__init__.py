from zope.component import getUtility, queryUtility

# Import "MessageFactory" to create messages in the plone domain
from zope.i18nmessageid import MessageFactory
PloneMessageFactory = MessageFactory('plone')
GMConvergenceMF = MessageFactory('gomobile.convergence')

import monkeypatch # Run navtree monkey patches
import indexing
import Missing

from interfaces import IConvergenceSupport

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
