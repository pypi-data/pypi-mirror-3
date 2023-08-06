"""

    Define mechanism for creating editable override field value proxies.
    
    http://mfabrik.com

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@mfabrik.com>'
__author_url__ = "http://mfabrik.com"
__docformat__ = 'epytext'
__copyright__ = "2009-2010 mFabrik Research Oy"
__license__ = "GPL v2"

import zope.interface
import zope.component
import zope.schema
from z3c.form import button
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAnnotations

from five import grok

from Products.CMFCore.interfaces import IContentish
from persistent import Persistent

from plone.directives import form
from zope.schema.interfaces import IContextSourceBinder

from gomobile.convergence.interfaces import IOverrider, IOverrideEditView, IOverrideForm
from gomobile.convergence.utilities import make_terms

from gomobile.convergence import GMConvergenceMF as _


_internal_methods = []

def internal(func):
    """ Mark method so that it should not go to the proxied object. """
    _internal_methods.append(func.__name__)
    return func

class Overrider(object):
    """
    Base class for mobile overrides.

    Checks if

    - The field is on "enabled overrides" list

    - Read the field value from mobile overrides instead of the proxyed real object

    The adapter look up uses standard view properties.

    We use underscore to mark functions and attributes which are not proxied
    from the orignal object in any scenario.

    Note that we need special magic for strings: Internally
    we manage them as unicode, but Archetypes-like interface assumes
    Title(), Description() etc. return UTF-8.
    """

    zope.interface.implements(IOverrider)

    # zope.schema object describing overriden fields
    _schema = None
    
    @internal
    def __init__(self, context):
        self.context = context

        
    @internal
    def _getOverrideFieldNames(self):
        return zope.schema.getFieldNamesInOrder(self._schema)
    
    @internal
    def _isOverride(self, fieldName):
        """
        @return True: If the field is overridable field
        """
        return fieldName in self._getOverrideFieldNames()
    
    @internal
    def _isOverrideEnabled(self, fieldName, storage):
        """
        Check whether the fieldName appears in "overrided fields list"
        """
        overrides = storage.enabled_overrides
        return fieldName in overrides

    @internal
    def _fixCallable(self, fieldName, value):

        # Check whether the orignal accessed attribute
        # was callable or not, so we can use
        # the same mechanism to override methods and attributes

        def callable_proxy():
            """ Faux generated function to return the overridden value when accessed as function """
            return value

        orignal = getattr(self.context, fieldName)
        if callable(orignal):
            return callable_proxy
        else:
            return value

    @internal
    def _getOverrideOrOrignal(self, fieldName):
        """
        """
        if self._isOverride(fieldName):

            storage = IOverrideStorage(self.context)

            if self._isOverrideEnabled(fieldName, storage):
                value = getattr(storage, fieldName)
                if value != None:
                    return self._fixCallable(fieldName, value)

        # Fall back to orignal field value
        return getattr(self.context, fieldName)

    @internal
    def __str__(self):
        return "Mobile overrides proxy object for %s" % str(self.context)

    def __getattr__(self, name):
        """ Proxy magic.
                    
        """
        
        if name in "cooked_text":
            import pdb ; pdb.set_trace()
        
        if name in _internal_methods:    
            return self.__dict__[name]
        else:
            return self._getOverrideOrOrignal(name)


class IOverrideFields(zope.interface.Interface):
    """
    Marker interface describing schema for overridden fields.
    """

@grok.provider(IContextSourceBinder)
def get_field_list(context):
    """ Return available overridable fields for mobile

    @param context: OverrideStorage subclass instance
    """

    schema = IOverrideFields(context)

    fields = zope.schema.getFieldsInOrder(schema)

    terms = [ SimpleTerm(value=name, token=name, title=field.title) for name, field in fields ]

    return SimpleVocabulary(terms)

from z3c.form.browser.checkbox import CheckBoxWidget, CheckBoxFieldWidget
class IOverrideFormSchema(form.Schema):
    """ Base class for editable override forms """

    form.widget(enabled_overrides=CheckBoxFieldWidget)
    enabled_overrides = zope.schema.List(title=_(u"Overridden fields"), required=False,
                                         value_type = zope.schema.Choice(source=get_field_list),
                                         default=[]
                                         )


class IOverrideStorage(zope.interface.Interface):
    """
    Adapter to store mobile overrides on context objects.

    You can override this adapter to
    store data in different database, for example.
    """

class OverrideStorage(Persistent):
    """
    Persistent object storing z3c.form field values for mobile overrides.

    Field values are attributes of this.

    - Attribute name is the name of the overriden field (like description)

    - Attribute value is the overriden value for the field
    """
    KEY = "mobile_override_values"

    zope.interface.implements(IOverrideFormSchema)

    enabled_overrides = FieldProperty(IOverrideFormSchema["enabled_overrides"])

def getOverrideStorage(context, storage_class=OverrideStorage):
    """ Default implementation how to store mobile overridden values for context objects.

    Use zope.annotations package to stick data on __annotations__ attribute on the object.

    @param context: Any plone content object

    @param storage: Storage class implementation we need to construct if this is first time accessing the storage
    """

    # Aqwrappers are evil
    context = context.aq_inner

    annotations = IAnnotations(context)

    value = annotations.get(storage_class.KEY, None)
    if value is None:
        # Compute value and store it on request object for further look-ups
        value = annotations[storage_class.KEY] = storage_class()

    return value

#class OverrideForm(form.SchemaEditForm):
class OverrideForm(form.SchemaForm):
    """ Site editor interface for mobile override attributes.
    """
    ignoreContext = False

    grok.baseclass()
    grok.context(IContentish)

    zope.interface.implements(IOverrideForm)

    schema = IOverrideFormSchema

    def __init__(self, context, request):
        """ Construct the form.

        """
        self.context = context
        self.request = request

    def getContent(self):
        """
        Adapt for the storage storing override data.
        """
        return IOverrideStorage(self.context)
    
    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
