"""

    Mobile override for templated document

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

import zope.interface
from zope import schema
from zope.schema.fieldproperty import FieldProperty

from five import grok
from plone.directives import form
from plone.app.z3cform.layout import wrap_form

from gomobile.convergence.overrider.base import getOverrideStorage
from gomobile.convergence.overrider import document as base

from collective.easytemplate.interfaces import ITemplatedDocument

from z3c.form.browser.textarea import TextAreaFieldWidget

class TemplatedDocumentOverrideSchema(base.DocumentOverrideSchema):

    getUnfilteredTemplate = schema.Text(title=u"Templated text")

class TemplatedDocumentOverrider(base.DocumentOverrider):
    """ Provide mobile specific versions for title, description and text Document.

    Document is Products.ATContentTypes.content.document.ATDocument object.
    """

    _schema = TemplatedDocumentOverrideSchema

def get_field_schema(context):
    """ Adapter to return schema telling which fields can be overridden

    @param context: TemplatedDocumentOverrideSettings persistent instance
    """
    return TemplatedDocumentOverrideSchema

class IFormSchema(base.IFormSchema):

    form.widget(getUnfilteredTemplate=TextAreaFieldWidget)
    getUnfilteredTemplate = schema.Text(title=u"Templated text", required=False)

class TemplatedDocumentOverrideStorage(base.DocumentOverrideStorage):
    """ Store document content type specific override settings
    """
    zope.interface.implements(IFormSchema)

    getUnfilteredTemplate = FieldProperty(IFormSchema["getUnfilteredTemplate"])


def storage_factory(context):
    """ Adapter which creates the persistent object storing document specific overrides.

    """
    return getOverrideStorage(context, TemplatedDocumentOverrideStorage)

class TemplatedDocumentOverriderForm(base.DocumentOverriderForm):
    """ Edit mobile overrides for the document
    """

    # This form is availalbe for this content type only
    grok.context(ITemplatedDocument)

    # Use plone.autoform way to construct fields (instead of z3c.form.field.Fields())
    schema = IFormSchema

    def updateWidgets(self):
        """ A method responsible for creating and setting up widgets in z3c.form.

        """
        # Call parent to do the initial widget set up work
        base.DocumentOverriderForm.updateWidgets(self)

        widget = self.widgets["getUnfilteredTemplate"]

        # Set <textarea> dimensions
        widget.cols = 40
        widget.rows = 80

TemplatedDocumentOverriderFormView = wrap_form(TemplatedDocumentOverriderForm)