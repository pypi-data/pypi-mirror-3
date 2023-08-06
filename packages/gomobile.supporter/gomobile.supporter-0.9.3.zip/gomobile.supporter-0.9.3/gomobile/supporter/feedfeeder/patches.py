"""

    Monkey patches for feedfeeder to make HTML mobile safe.

"""

__license__ = "GPL 2"
__copyright__ = "2020 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__docformat__ = "epytext"

import logging

import lxml.html
from lxml.etree import ParserError

from zope.app.cache import ram

from Products.feedfeeder.content.item import FeedFeederItem

logger = logging.getLogger("GoMobile")

logger.info("Running in feedfeeder monkey-patches")

# Cache storing transformed XHTML
xhtml_cache = ram.RAMCache()
xhtml_cache.update(maxAge=600, maxEntries=1000)

# Dummy object to mark missing values from cache
_marker = object()

def cache(name):
    """ Special cache decorator which generates cache key based on context object and cache name """
    def decorator(fun):
        def replacement(context):
            key = str(context.UID()) + "." + name

            cached_value = xhtml_cache.query(key, default=_marker)
            if cached_value is _marker:
                cached_value = fun(context)
                xhtml_cache.set(cached_value, key)
            return cached_value
        return replacement
    return decorator

def clean_html(context, request, html):
    """
    """
    from zope.component import getMultiAdapter

    mobile_image_html_rewriter = getMultiAdapter((context, request), name="mobile_image_html_rewriter")
    return mobile_image_html_rewriter.processHTML(html, trusted=False, only_for_mobile=False)


def flush_cache(name, context):
    """ Clear entry in RAMCache

    global_key is function specific key, key is context specific key.

    """
    if context.UID() is None:
        return

    if name is None:
        return

    key = context.UID() + "." + name
    xhtml_cache.invalidate(key)


#
# Modify existing body text and description accessors so that
# 1) HTML is cleaned
# 2) The result cleaned HTML is cached in RAM
#
# We do not persistently want to store cleaned HTML,
# since our cleaner might be b0rked and we want to easily
# regenerate cleaned HTML when needed.
#

# Run in monkey patching
FeedFeederItem._old_getText = FeedFeederItem.getText
FeedFeederItem._old_setText = FeedFeederItem.setText
FeedFeederItem._old_Description = FeedFeederItem.Description
FeedFeederItem._old_setDescription = FeedFeederItem.setDescription

@cache("text")
def _getText(self):
    """ Body text accessor """

    try:
        text = FeedFeederItem._old_getText(self)
    except UnicodeEncodeError:
        return "Bad unicode"

    if text:
        # can be None
        request = self.REQUEST
        clean = clean_html(self, request, text)
        return clean

    return text

def _setText(self, value, *args, **kwargs):
    FeedFeederItem._old_setText(self, value, *args, **kwargs)
    flush_cache("text", self)

@cache("description")
def _Description(self):
    """ Description accessor """
    text = FeedFeederItem._old_Description(self)

    #print "Accessing description:" + str(text)

    # Remove any HTML formatting in the description
    if text:
        try:
            parsed = lxml.html.fromstring(text.decode("utf-8"))
        except ParserError:
            # Empty document and so on
            return u""

        clean = lxml.html.tostring(parsed, encoding="utf-8", method="text").decode("utf-8")
        #print "Cleaned decsription:" + clean
        return clean

    return text

def _setDescription(self, value):
    FeedFeederItem._old_setDescription(self, value)
    flush_cache("description", self)

FeedFeederItem.getText = _getText
FeedFeederItem.setText = _setText
FeedFeederItem.Description = _Description
FeedFeederItem.setDescription = _setDescription
