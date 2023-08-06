"""

    Mobile override for templated document

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

import logging

from five import grok

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from gomobile.convergence.interfaces import IOverrider
from gomobile.convergence.overrider.base import IOverrideStorage

from collective.easytemplate.config import *
from collective.easytemplate import interfaces
from collective.easytemplate.engine import getEngine, getTemplateContext
from collective.easytemplate.utils import outputTemplateErrors, logTemplateErrors

from collective.easytemplate.content.TemplatedDocument import ERROR_MESSAGE, logger

from collective.easytemplate.interfaces import ITemplatedDocument

grok.templatedir("templates")

class EasyTemplateMobile(grok.View):
    """ Enable viewing of templated pages with mobile overrides
    """

    grok.require("zope2.View") # TODO: How to make grok accept permissions as pseudo-constants
    grok.context(ITemplatedDocument)

    def __init__(self, context, request):
        grok.View.__init__(self, context, request)

        self.overrider = IOverrider(self.context)

    def title(self):
        """
        """
        return self.overrider.Title()

    def description(self):
        """
        """
        return self.overrider.Description()

    def cooked_text(self):
        """
        @return: Resulting HTML of evaluated template
        """
        return self._cookTemplate()

    def outputTemplateErrors(self, messages):
        """ Write template errors to the user and the log output. """
        outputTemplateErrors(messages, request=self.request, logger=logger, context=self.context)

    def getTemplateSource(self):
        """ Try look up what text box we use for mobile rendering

        1. Mobile "raw template" input

        2. Mobile WYSIWYG

        3. Generic raw template

        4. Generic WYWIWYG

        """

        storage = IOverrideStorage(self.context)

        # TODO: Bad API, will be changed
        if self.overrider._isOverrideEnabled("getUnfilteredTemplate", storage):
            # Raw HTML code for mobile
            text = self.overrider.getUnfilteredTemplate()
        elif self.overrider._isOverrideEnabled("getText", storage):
            # WYSIWYG HTML code for mobile
            text = self.overrider.getText()
        else:
            # Choose between normal kupu editor input
            # and unfiltered input
            unfiltered = self.context.getRawUnfilteredTemplate()

            if unfiltered != None and unfiltered.strip() != "":
                # We are using raw HTML input
                text = unfiltered.decode("utf-8")
            else:
                text = self.context.getText().decode("utf-8")

        return text

    def compile(self, text):
        """ Compile the template. """
        engine = getEngine()

        if text == None:
            text = ""

        # TODO: Compile template only if the context has been changed
        t, messages = engine.loadString(text, False)
        return t, messages


    def _cookTemplate(self):
        """ Cook the view mode output. """

        context = getTemplateContext(self.context)

        text = self.getTemplateSource()
        t, messages = self.compile(text)

        self.outputTemplateErrors(messages)
        if not t:
            return ERROR_MESSAGE

        output, messages = t.evaluate(context)
        self.outputTemplateErrors(messages)
        if not output:
            return ERROR_MESSAGE

        return unicode(output).encode("utf-8")



