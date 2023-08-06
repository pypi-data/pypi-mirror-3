c__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import unittest

import zope.interface
from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.statusmessages.interfaces import IStatusMessage

from gomobile.convergence.interfaces import IOverrider
from gomobile.convergence.overrider.base import IOverrideStorage
from gomobile.convergence.tests.base import BaseTestCase
from gomobiletheme.basic.tests import MOBILE_HTML_MARKER
from collective.easytemplate.tests.base import EasyTemplateTestCase
from gomobile.mobile.interfaces import IMobileLayer
from gomobile.mobile.tests.utils import ZCML_INSTALL_TEST_DISCRIMINATOR

@onsetup
def setup_zcml():

    fiveconfigure.debug_mode = True
    import gomobile.suppoter.easytemplate

    import collective.easytemplate
    zcml.load_config('configure.zcml', gomobile.suppoter)
    zcml.load_string(ZCML_INSTALL_TEST_DISCRIMINATOR)


    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('gomobile.mobile')
    ztc.installPackage('gomobile.convergence')
    ztc.installPackage('gomobiletheme.basic')
    ztc.installPackage('collective.easytemplate')
    ztc.installPackage('gomobile.supporter.easytemplate')

    fiveconfigure.debug_mode = False


ptc.setupPloneSite(products=['gomobile.mobile', 'gomobile.convergence', 'gomobiletheme.basic', "collective.easytemplate", "gomobile.suppoter.easytemplate", 'gomobiletheme.basic'],
                   extension_profiles=['Products.CMFPlone:testfixture'])

class TestEasyTemplateOverrides(BaseTestCase):
    """
    Check that "mobile overrides" feature functions for easy template content.
    """
    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)
        self._refreshSkinData()
        self.setDiscriminateMode("mobile")



    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("TemplatedDocument", "doc")
        self.portal.doc.setCatchErrors(True)

    def assertNoEasyTemplateErrors(self):
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()
        for m in messages:
            print str(m.message)

        self.assertEqual(len(messages), 0)


    def test_has_overrides(self):
        """ Document object overrides are enabled by default
        """
        self.create_doc()
        doc = self.portal.doc
        overrider = IOverrider(doc)
        assert overrider != None

        assert overrider.schema != None
        self.assertEqual(overrider._getOverrideFieldNames(), ["Title", "Description", "getText", "getUnfilteredTemplate"])

        # Set one override enabled and check it is read properly
        storage = IOverrideStorage(doc)

        storage.enabled_overrides = ["Title"]
        self.assertEqual(overrider._isOverrideEnabled("Title", storage), True)
        self.assertEqual(overrider._isOverrideEnabled("Description", storage), False)

        # Set overriden title
        storage.Title = u"Foobar"

        # Call title accessor by emulator IOverrider steps
        # and see each microstep completes
        self.assertTrue(overrider._isOverride("Title"))
        storage = IOverrideStorage(self.portal.doc)
        self.assertTrue(overrider._isOverrideEnabled("Title", storage))
        self.assertEqual(overrider._getOverrideOrOrignal("Title")(), u"Foobar")

        assert overrider.Title() == u"Foobar"


    def test_override_template(self):
        """
        """
        self.create_doc()
        doc = self.portal.doc
        overrider = IOverrider(doc)

        doc.setTitle("Foobar")

        template = u"Title {{ context.Title() }}"
        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["getUnfilteredTemplate"]
        storage.getUnfilteredTemplate = template

        self.assertEqual(overrider.getUnfilteredTemplate(), template)

    def test_override_not_enabled(self):
        """ Do not enable override, but have the field filled in
        """

        self.setDiscriminateMode("web")

        self.create_doc()
        doc = self.portal.doc
        overrider = IOverrider(doc)

        doc.setTitle("Foobar")

        template = u"Title {{context.Title()}}"
        storage = IOverrideStorage(doc)
        storage.getUnfilteredTemplate = template

        self.assertNotEqual(overrider.getUnfilteredTemplate(), template)


    def test_convergence_form(self):
        self.setDiscriminateMode("web")

        self.create_doc()

        result = self.portal.doc.restrictedTraverse("@@convergence")

        self.assertEqual(result.media_status(), u"Web and mobile")

        # Test rendeing HTML without errors
        result()

class BrowingTestCase(ptc.FunctionalTestCase):

    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("TemplatedDocument", "doc")
        self.portal.doc.setCatchErrors(True)

    def setDiscriminateMode(self, mode):
        """
        Spoof the following HTTP request media.

        @param: "mobile", "web" or other MobileRequestType pseudo-constant
        """

        from gomobile.mobile.tests.utils import TestMobileRequestDiscriminator
        TestMobileRequestDiscriminator.setModes([mode])

        # skin manager must update active skin for the request
        self._refreshSkinData()

    def setUp(self):
        ptc.FunctionalTestCase.setUp(self)

        # Enable unit test friendly errors

        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

        from Products.Five.testbrowser import Browser

        self.browser = Browser()
        self.browser.handleErrors = False

    def test_cooked_web_template(self):
        """ See that web templates are cooked for mobile unless explictly overriden
        """
        self.create_doc()
        doc = self.portal.doc
        doc.setTitle("Foobar")
        doc.setText("Title {{ context.Title() }}")

        self.setDiscriminateMode("mobile")
        cooked = doc.getTemplatedText()
        self.assertTrue("Title Foobar" in cooked, cooked)

        self.browser.open(doc.absolute_url())
        html = self.browser.contents

        self.assertTrue(MOBILE_HTML_MARKER in html) # See that we are rendering mobile mode
        self.assertTrue("Title Foobar" in html)

    def test_cooked_mobile_template(self):
        """ Check that mobile specific template is rendered for mobile.
        """
        self.create_doc()
        doc = self.portal.doc


        overrider = IOverrider(doc)

        doc.setTitle("Foobar")

        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["getUnfilteredTemplate"]
        storage.getUnfilteredTemplate = u"Title {{ context.Title() }}"

        self.setDiscriminateMode("mobile")
        zope.interface.alsoProvides(self.portal.REQUEST, IMobileLayer)

        # This should be views.EasyTemplateMobileView
        self.browser.open(self.portal.doc.absolute_url())
        html = self.browser.contents

        if "The page structure contains errors" in html:

            messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()

            if messages:
                for m in messages: print str(m.message)


            raise RuntimeError("Bad templated page")

        self.assertTrue(MOBILE_HTML_MARKER in html) # See that we are rendering mobile mode
        self.assertTrue("Title Foobar" in html)

    def test_cooked_mobile_template_should_not_appear_web(self):
        """
        Even if we set mobile override template, it should not affect web viewing any how.
        """
        self.create_doc()
        doc = self.portal.doc
        overrider = IOverrider(doc)

        doc.setTitle("Foobar")

        storage = IOverrideStorage(doc)
        storage.getUnfilteredTemplate = u"Title {{ context.Title() }}"

        self.setDiscriminateMode("web")
        self.browser.open(self.portal.doc.absolute_url())
        html = self.browser.contents # This should be document_view.pt
        print html
        self.assertFalse(MOBILE_HTML_MARKER in html) # See that we are rendering mobile mode
        self.assertFalse("Title Foobar" in html) # In web we do not run the snippet


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEasyTemplateOverrides))
    suite.addTest(unittest.makeSuite(BrowingTestCase))
    return suite



