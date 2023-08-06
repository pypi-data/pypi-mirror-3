"""
    Suppoer behavior assignments for non-dexerity objects.

    Define default mechanism to determine whether thr header animation
    is enabled (the header is editable) on content.

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

import zope.interface
import zope.component
from zope import schema
from five import grok
from zope.schema.fieldproperty import FieldProperty

from Products.ATContentTypes.interface import IATDocument

from plone.directives import form
from plone.app.z3cform.layout import wrap_form
from z3c.form import field

from gomobile.convergence.overrider import base
from gomobile.convergence.utilities import addSchema
from gomobile.convergence import GMConvergenceMF as _

from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

class DocumentOverrideSchema(form.Schema):
    """ Schema for overriden accessors.

    Correspond AT accessor names for  Products.ATContentTypes.content.document.ATDocumentSchema.
    """
    Title = schema.TextLine(title=_(u"Title"))

    Description = schema.Text(title=_(u"Description"))

    getText = schema.Text(title=_(u"Text"))


def get_field_schema(context):
    """ Adapter to return schema telling which fields can be overridden

    @param: DocumentOverrideSettings persistent instance
    """
    return DocumentOverrideSchema


class DocumentOverrider(base.Overrider):
    """ Provide mobile specific versions for title, description and text Document.

    Document is Products.ATContentTypes.content.document.ATDocument object.
    """

    _schema = DocumentOverrideSchema

class IFormSchema(base.IOverrideFormSchema):
    """ Schema for "edit mobile overrides" form """

    Title = schema.TextLine(title=_(u"Title"), required=False)

    Description = schema.Text(title=_(u"Description"), required=False)

    form.widget(getText=WysiwygFieldWidget)
    getText = schema.Text(title=_(u"Text"), required=False)


class DocumentOverrideStorage(base.OverrideStorage):
    """ Store document content type specific override settings
    """
    zope.interface.implements(IFormSchema)

    Title = FieldProperty(IFormSchema["Title"])
    Description = FieldProperty(IFormSchema["Description"])
    getText = FieldProperty(IFormSchema["getText"])


def document_override_storage_factory(context):
    """ Adapter which creates the persistent object storing document specific overrides.

    """
    return base.getOverrideStorage(context, DocumentOverrideStorage)

class DocumentOverriderForm(base.OverrideForm):
    """ Edit mobile overrides for the document
    """

    grok.context(IATDocument)

    schema = IFormSchema

DocumentOverriderFormView = wrap_form(DocumentOverriderForm)
