"""

    Convergence options and content support interfaces.

"""

__license__ = "GPL 2"
__copyright__ = "2009-2010 mFabrik Research Oy"

from zope import schema
from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

from plone.browserlayer.interfaces import ILocalBrowserLayerType

#from collective.contentleadimage import LayoutImageMessageFactory as _
from z3c.form.interfaces import IForm

from zope.publisher.interfaces.browser import IBrowserView

class ContentMediaOption(object):
    """ Pseudo-constants defining on which medias content should apper """
    WEB = "web"
    MOBILE = "mobile"
    USE_PARENT = "parent"
    BOTH = "both" # default

class IConvergenceSupport(Interface):
    """ The content supports convergence options """


class IConvergenceMediaFilter(Interface):
    """ Utility to deal with the media state of content objects and catalog brains. """

class IConvergenceBrowserLayer(Interface):
    """ This layer is applied on the request when Go Mobile Convergenced add on is installed.

    It will have effects on 
    
    * sitemap
    
    * portal_tabs
    
    * portal breadcrumbs
    """

class IOverrider(Interface):
    """ Override content fields to have mobile specific values for mobile phones.

    This interface provides view-like adapter look-up to extract mobile specific
    values from the content. For example, you might want to have different
    body text for web and mobile.

    This interface is indended to provide read-only access to mobile specific overrides
    and allow easy way to drop-in mobile specific replacements for various content object views.

    The adapter is just a dumb proxy object which redirects accessors for
    mobile specific versions if present.

    The actual mobile specific field data is stored on the content specific
    annotatios.

    The mobile overrides are not effective for catalog look-up based
    operations like getting the content title in the folder listing.


    How to use
    ----------

    Normally you would read the context description like this::

        desc = context.getDescription()

    But if you want to have mobile override for description if it's
    enabled you do like this::

        context = IMobileOverrider(context)
        desc = context.getDescription()
        # desc will be mobile overriden description if one is available

    You can also check whether the context object supports mobile overrides:

        new_context = IMobileOverrider(context)
        if new_context is context:
            # No mobile overrides
        else:
            # We get new, proxied, context


    """

class IOverrideForm(IForm):
    """ Form definition for field-specific override editing.
    
    Each content type can have its own form.
    Used as an adapter.
    """

class IOverrideEditView(IBrowserView):
    """ Provide form access to edit mobile overrides.

    A view which does site editor enabled editing of mobile overrides.

    Must honour the view name "edit_mobile_overrides"
    """




