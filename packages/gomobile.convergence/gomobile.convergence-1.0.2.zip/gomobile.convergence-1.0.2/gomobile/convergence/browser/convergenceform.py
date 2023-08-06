"""

    Convergence options edit forms.
    
    This will override gomobile.mobile Mobile options form
    by overriding document_actions "mobile_options" action
    when quick installer is run (actions.xml)

    http://mfabrik.com
    
"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = "epytext"

import copy
import os

from Acquisition import aq_inner
import zope.interface
from zope import schema
from zope.component import getUtility, queryUtility, ComponentLookupError
from zope.component import getMultiAdapter, queryMultiAdapter
from Products.Five.browser import BrowserView

import z3c.form.form
from z3c.form import subform
from z3c.form import field
from z3c.form import group
from z3c.form import button

from gomobile.convergence.interfaces import IOverrideForm, IOverrider
from plone.z3cform.layout import FormWrapper, wrap_form

try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPER_FORM = True
except ImportError:
    HAS_WRAPPER_FORM = False # Old plone.z3cform version
    
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from gomobile.mobile.behaviors import IMobileBehavior 
from gomobile.mobile.browser.forms import MobileForm

from gomobile.convergence.behaviors import contentMediasVocabury, IMultiChannelBehavior, multichannel_behavior_factory
from gomobile.convergence.interfaces import ContentMediaOption, IConvergenceMediaFilter, IConvergenceBrowserLayer
from gomobile.convergence.filter import media_options_vocabulary
from gomobile.convergence.interfaces import IOverrideForm

from gomobile.convergence.overrider.base import IOverrideStorage

from gomobile.convergence import GMConvergenceMF as _
from gomobile.convergence.filter import getConvergenceMediaFilter

class PublishingForm(z3c.form.form.EditForm):
    """ Folder/page specific convergence options """

    fields = field.Fields(IMultiChannelBehavior)

    prefix = "publishing"
    label = _(u"Media options")

    def update(self):
        return z3c.form.form.EditForm.update(self)
    
    def getContent(self):
        """
        """
        behavior = IMultiChannelBehavior(self.context)
        return behavior        

    def applyChanges(self, data):
        # Call super
        val = z3c.form.form.EditForm.applyChanges(self, data)

        # Write behavior to database
        self.getContent().save()
        
        return val


class OverrideForm(z3c.form.form.EditForm):
    """ Fielde specific convergence options """


    label = _(u"Field overrides")
    prefix = "overrides"

    def __init__(self, context, request, content_object):
        self.context = context
        self.request = request
        self.content_object = content_object

    def update(self):
        """ Dynamically load fields.

        Form.update() is correct place to fiddle
        with fields information, before proceeding
        to parent update() and widget creation.
        """

        self.fields = self.getOverriderFields()
        z3c.form.form.EditForm.update(self)

    def getOverriderFields(self):
        """ Recycle fields dynamically from another form instance """

        # Get the mobile overrider form for the context
        form = getMultiAdapter((self.content_object, self.request), IOverrideForm)

        # Read its Fields instance
        fields = form.fields
        # Fields could be mofified in this point
        # (need to duplicate it first though)

        return fields

class MasterForm(z3c.form.form.EditForm):
    """ Bring together three different mobile related settings forms. """
    
    name = "mobile-settings"
    label = _(u"Mobile settings")

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        """ Delegate Save button press to individual form handlers.
        """
        
        # buttonAndHandler decorator has converted the actual button methods to Handler instances
        # they take arguments (form, action)
        self.publishing_form_instance.handleApply(self.publishing_form_instance, action)
        
        self.mobile_form_instance.handleApply(self.mobile_form_instance, action)
        
        if self.override_form_instance is not None:
            self.override_form_instance.handleApply(self.mobile_form_instance, action)
        
        # Make sure no funny redirects happen
        
        self.status = self.successMessage

    def convertToSubForm(self, form_instance):
        """
        Make existing form object behave like subform object.
        
        * Do not render <form> frame
            
        * Do not render actions
    
        @param form_instance: Constructed z3c.form.form.Form object
        """

        # Create mutable copy which you can manipulate
        form_instance.buttons = copy.deepcopy(form_instance.buttons)
        
        # Remove subform action buttons using dictionary style delete
        for button_id in form_instance.buttons.keys():
            del form_instance.buttons[button_id]

        if HAS_WRAPPER_FORM:
            # Plone 4 / Plone 3 compatibility
            zope.interface.alsoProvides(form_instance, IWrappedForm)        

        # Use subform template - this prevents getting embedded <form>
        # elements inside the master <form>
        import plone.z3cform
        from zope.app.pagetemplate import ViewPageTemplateFile as Zope3PageTemplateFile
        from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate
        template = Zope3PageTemplateFile('subform.pt', os.path.join(os.path.dirname(plone.z3cform.__file__), "templates"))        
        form_instance.template = BoundPageTemplate(template, form_instance)


    def update(self):
        """ Constructor embedded sub forms """
                
        # Construct few embedded forms
        self.mobile_form_instance = MobileForm(self.context, self.request)
        
        self.publishing_form_instance = PublishingForm(self.context, self.request)        

        # Hide form buttons
        self.convertToSubForm(self.mobile_form_instance)
        self.convertToSubForm(self.publishing_form_instance)


        self.mobile_form_instance.update()
        self.publishing_form_instance.update()
        
        # Override form is present only if the content supports overrideable settings
        try:
            self.override_form_instance = getMultiAdapter((self.context, self.request), IOverrideForm)
            self.override_form_instance.update()
            self.convertToSubForm(self.override_form_instance)
            
        
        except ComponentLookupError:
            # This component doesn't support field overrides
            self.override_form_instance = None
        
        z3c.form.form.EditForm.update(self)

class MasterFormView(FormWrapper):
    
    form = MasterForm
    
    index = FiveViewPageTemplateFile("convergenceform.pt") 

    def media_status(self):
        """ Get human-readable text on which medias the context is available  """
        
        context = self.context.aq_inner
        
        filter = getConvergenceMediaFilter()
        media = filter.solveContentMedia(context)

        # Translate vocabulary
        for id, text in media_options_vocabulary:
            if id == media:
                return text

    def setSubformTemplate(self, form_instance):
        pass

    def render_override_form(self):
        """ Update and render one of forms on this view.

        Called by template.
        """
        return self.form_instance.override_form_instance()

    def render_publishing_form(self):
        """ Update and render one of forms on this view.

        Called by template."""
        return self.form_instance.publishing_form_instance()
    
    def render_mobile_form(self):
        
        self.setSubformTemplate(self.form_instance.mobile_form_instance)        
        return self.form_instance.mobile_form_instance()

    