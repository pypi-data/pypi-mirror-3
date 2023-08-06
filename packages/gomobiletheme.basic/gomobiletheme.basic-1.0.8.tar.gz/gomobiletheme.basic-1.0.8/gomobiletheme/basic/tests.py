"""

    Functional and unit tests for Go Mobile Default theme.

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@mfabrik.com>'
__docformat__ = 'epytext'
__copyright__ = "2010 mFabrik Research"
__license__ = "GPL v2"

from AccessControl import Unauthorized

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc
from zope.component import getUtility

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.PloneTestCase.layer import PloneSite


from gomobile.mobile.tests import utils as test_utils

from gomobile.mobile.interfaces import MobileRequestType, IMobileRequestDiscriminator, IMobileImageProcessor
from gomobile.mobile.tests.utils import TestMobileRequestDiscriminator
from gomobile.mobile.tests.utils import MOBILE_USER_AGENT
from gomobile.mobile.tests.utils import UABrowser
from gomobile.mobile.tests.utils import ZCML_INSTALL_TEST_DISCRIMINATOR

try: 
    # Plone 4 and higher 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3

# Which string marks output HTML pages that we are correctly rendered as mobile site
MOBILE_HTML_MARKER = 'HandheldFriendly'

# Which string marks output HTML pages that we are still on default Plone theme
PLONE_DEFAULT_HTML_MARKER = "Plone Foundation"

@onsetup
def setup_zcml():

    fiveconfigure.debug_mode = True
    import gomobiletheme.basic
    import gomobile.convergence
    zcml.load_config('configure.zcml', gomobiletheme.basic)
    
    # Need to explicitly declare depdendency on this 
    # so that we can run overrider tests 
    # (this is not natural dep for gomobiletheme.basic)
    zcml.load_config('configure.zcml', gomobile.convergence)
    zcml.load_string(ZCML_INSTALL_TEST_DISCRIMINATOR)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    ztc.installPackage('gomobile.mobile')
    ztc.installPackage('gomobile.convergence')
    ztc.installPackage('gomobiletheme.basic')

# The order here is important.
setup_zcml()
ptc.setupPloneSite(products=['gomobile.mobile', 'gomobile.convergence', "gomobiletheme.basic"])

class BaseTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

    def setUp(self):
        ptc.FunctionalTestCase.setUp(self)
        
    def afterSetUp(self):
        self.initializeLogger()    
        self.installMobileTheme(self.getProductName())
    
    def getProductName(self):
        """ Subclass can override """
        return "gomobiletheme.basic"
    
    def installMobileTheme(self, name):
        """
        This will force Go Mobile Default Theme to be active
        as it seems that if other theme packages are present
        when running tests over many packages,
        the functional test state is not reset between
        packages and we have crap as mobile_properties.mobile_skin name
        instead of Go Mobile Default Theme
        TODO: This could be fixed using test layers?
        """
        
        qi = self.portal.portal_quickinstaller
        
        try:
            qi.uninstallProducts([name])
        except:
            pass
        qi.installProduct(name)
        

    def initializeLogger(self):
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
    
    def setDiscriminateMode(self, mode):
        """
        Spoof the following HTTP request media.

        @param: "mobile", "web" or other MobileRequestType pseudo-constant
        """
        TestMobileRequestDiscriminator.setModes([mode])

        # skin manager must update active skin for the request
        self._refreshSkinData()
        
    def setUA(self, user_agent):
        """
        Create zope.testbrowser Browser with a specific user agent.
        """

        # Be sure to use Products.Five.testbrowser here
        self.browser = UABrowser(user_agent)
        self.browser.handleErrors = False # Don't get HTTP 500 pages
                
    def useMobileMode(self):
        self.setDiscriminateMode(MobileRequestType.MOBILE)

    def useWebMode(self):
        self.setDiscriminateMode(MobileRequestType.WEB)

    def assertNotDefaultPloneTheme(self, html):
        self.assertFalse(PLONE_DEFAULT_HTML_MARKER in html, "The rendered page used default Plone theme")

    def loginAsAdmin(self):
        """ Perform through-the-web login.

        Simulate going to the login form and logging in.

        We use username and password provided by PloneTestCase.

        This sets session cookie for testbrowser.
        """
        from Products.PloneTestCase.setup import portal_owner, default_password

        # Go admin
        browser = self.browser
        browser.open(self.portal.absolute_url() + "/login_form")
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()

class ThemeTestCase(BaseTestCase):
    """
    Test gomobiletheme.basic functionality.
    """

    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)
        self._refreshSkinData()

    def prepare_render(self, object):
        """
        Render page both logged in and logged out.

        The object must implement simple workflow and must not be published.

        """

        self.browser.open(object.absolute_url())

        return self.browser.contents

    def test_installed(self):
        """ Check that we are installed
        """
                
        # Check theme is selected in mobile settings
        mobile_properties = self.portal.portal_properties.mobile_properties

        self.assertEqual(mobile_properties.mobile_skin, "Go Mobile Default Theme")


        # Check that our main_template layer is available
        skins = self.portal.portal_skins
        self.assertTrue("gomobiletheme_basic" in skins.objectIds(), "Had skin layers " + str(skins.objectIds()))

    def test_load_resource(self):
        """
        See that our static resources are loaded correctly.
        """

        file = "++resource++gomobiletheme.basic/logo.gif"

        #self.browser.open(self.portal.absolute_url() +"/" + file)
        #self.assertEqual(self.browser.headers["content-type"], "image/gif")
        pass

    def test_render_main_template(self):
        """
        Render main template in mobile mode
        """
        self.setDiscriminateMode(MobileRequestType.MOBILE)

        html = self.prepare_render(self.portal)

        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)

    def test_render_web_mode(self):
        """
        Check that Plone renders page normally if not in mobile mode
        """
        self.setDiscriminateMode(MobileRequestType.WEB)
        utility = getUtility(IMobileRequestDiscriminator)
        html = self.prepare_render(self.portal)

        self.assertFalse(MOBILE_HTML_MARKER in html, "Got page:" + html)

    def test_render_page(self):
        """ Assert no exceptions risen """

        self.setDiscriminateMode(MobileRequestType.MOBILE)

        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "page")

        object = self.portal.page
        self.portal.portal_workflow.doActionFor(object, "submit")
        self.portal.portal_workflow.doActionFor(object, "publish")

        self.setDiscriminateMode(MobileRequestType.MOBILE)

        html = self.prepare_render(self.portal.page)

    def test_render_folder(self):
        """ Assert no exceptions risen """

        self.setDiscriminateMode(MobileRequestType.MOBILE)

        self.loginAsPortalOwner()
        self.portal.invokeFactory("Folder", "folder")

        object = self.portal.folder
        #self.portal.portal_workflow.doActionFor(object, "submit")
        self.portal.portal_workflow.doActionFor(object, "publish")

        self.setDiscriminateMode(MobileRequestType.MOBILE)

        html = self.prepare_render(self.portal.folder)

    def test_render_login(self):
        """ Assert no exceptions risen when we are rendering old fashioned page template and HTTP POST """

        from Products.PloneTestCase.setup import portal_owner, default_password
         # Go admin
        browser = self.browser
        browser.open(self.portal.absolute_url() + "/login_form")

        html = browser.contents
        self.assertNotDefaultPloneTheme(html)
        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)

        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()

        html = browser.contents
        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)

    def test_mobile_folder_listing(self):
        """ """
        from gomobiletheme.basic.viewlets import MobileFolderListing
        from gomobile.mobile.browser.views import FolderListingView

        # Soiif default template check
        from gomobile.mobile.tests.utils import spoofMobileFolderListingActiveTemplate
        spoofMobileFolderListingActiveTemplate()



        self.setDiscriminateMode(MobileRequestType.MOBILE)

        # Create a sample folder
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Folder", "folder")
        self.portal.folder.invokeFactory("Document", "page1")
        self.portal.folder.invokeFactory("Document", "page2")

        spoofMobileFolderListingActiveTemplate()

        # Get the viewlet
        viewlet = MobileFolderListing(self.portal.folder, self.portal.folder.REQUEST, None, None)
        self.assertNotEqual(viewlet, None, "Could not find mobilefolderlisting viewlet")

        viewlet.update()
        self.assertEqual(len(viewlet.items), 2)

        # Now set one of the pages as default
        #default_page_helper = getMultiAdapter((self.portal.folder, self.portal.REQUEST), name='default_page')
        #default_page_helper.
        self.portal.folder.default_page = "page1"
        viewlet.update()
        self.assertEqual(len(viewlet.items), 1)

    def test_empty_analytics(self):
        """ Render empty analytics viewlet """
        from gomobiletheme.basic.viewlets import MobileTracker
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        self.portal.portal_properties.mobile_properties.tracker_name = ""
        self.portal.portal_properties.mobile_properties.tracking_id = ""
        viewlet = MobileTracker(self.portal, self.portal.REQUEST, None, None)
        viewlet.update()
        viewlet.render()

    def test_admob_analytics(self):
        """ Render AdMob analytics code """
        from gomobiletheme.basic.viewlets import MobileTracker
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        self.portal.portal_properties.mobile_properties.tracker_name = "admob"
        self.portal.portal_properties.mobile_properties.tracking_id = "123"


        viewlet = MobileTracker(self.portal, self.portal.REQUEST, None, None)
        viewlet.update()
        viewlet.render()

    def test_render_empty_search_page(self):

        self.setDiscriminateMode(MobileRequestType.MOBILE)
      
        self.browser.open(self.portal.absolute_url() + "/search")

        
    def test_render_search(self):
        """ Assert no exceptions risen """
        
        self.setDiscriminateMode(MobileRequestType.MOBILE)
      
        self.browser.open(self.portal.absolute_url() + "/search")
        
        # Input some values to the search that we see we get
        # zero hits and at least one hit        
        for search_terms in [u"Plone", u"youcantfindthis"]:
            
            # XXX: Temporary fix to double form issue
            form = self.browser.getForm(name="searchform")
            
            # Fill in the search field
            input = form.getControl(name="SearchableText")
            input.value = search_terms 
            
            # Submit the search form
            form.submit(u"Search")
            

from zope.component import getMultiAdapter, getUtility

from gomobile.convergence.interfaces import IOverrider
from gomobile.convergence.overrider.base import IOverrideStorage

class TestMobileOverrides(BaseTestCase):
    """ Check that field level overrides are rendered correctly in mobile mode.

    TODO This should be moved to gomobile.convergence
    """

    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)
        self._refreshSkinData()

    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")

    def test_helper_view_mobile(self):
        """
        See that we get proper proxy object through helper view.
        """
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        self.create_doc()
        doc = self.portal.doc
        doc.setTitle("Not reached")
        overrider = IOverrider(doc)
        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["Title"]
        storage.Title = u"Foobar"

        helper = doc.restrictedTraverse("multichannel_overrider")
        context = helper() # Return mobile proxy object with overriden values

        # In mobile mode, you get override
        self.assertEqual(context.Title(), u"Foobar")

    def test_helper_view_web(self):
        """
        See that we get proper proxy object through helper view.
        """
        self.setDiscriminateMode(MobileRequestType.WEB)
        self.create_doc()
        doc = self.portal.doc
        doc.setTitle("Not reached")
        overrider = IOverrider(doc)
        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["Title"]
        storage.Title = u"Foobar"

        helper = doc.restrictedTraverse("multichannel_overrider")
        context = helper() # Return mobile proxy object with overriden values

        # In web mode, you dont get override
        self.assertEqual(context.Title(), "Not reached")

    def test_render_mobile_override(self):
        """ Render a document with mobile overrides enabled.

        """

        self.setDiscriminateMode("mobile")

        self.create_doc()
        doc = self.portal.doc
        doc.setTitle("Not reached") # This title should not be visible in mobile mode
        overrider = IOverrider(doc)
        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["Title"]
        storage.Title = u"Foobar"

        self.portal.portal_workflow.doActionFor(doc, "submit")
        self.portal.portal_workflow.doActionFor(doc, "publish")


        browser = self.browser
        browser.open(self.portal.doc.absolute_url())
        html = browser.contents

        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)
        assert "Foobar" in html

class TestPostPublication(BaseTestCase):
    """
    """

    def afterSetUp(self):
        self._refreshSkinData()

    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")

    def xxx_test_content_type(self):
        """
        Mobile profile not supported.

        See that we get proper proxy object through helper view.
        """
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        browser = self.browser
        browser.open(self.portal.absolute_url())

        CONTENT_TYPE = "application/vnd.wap.xhtml+xml"
        self.assertEqual(browser.headers["content-type"], CONTENT_TYPE)

class TestGAFunctional(BaseTestCase):
    """ Test Google Analytics tracking.
    
    TODO: Move this under gomobile.mobile tests.
    """ 

    def afterSetUp(self):
        
        BaseTestCase.afterSetUp(self)
                
        self.portal.portal_properties.mobile_properties.tracker_name = "google-mobile"
        
        # This id is updated in GA, manually check whether it gets hits or no
        self.portal.portal_properties.mobile_properties.tracking_id = "MO-8819100-7" #"UA-8819100-7"
        
        self.portal.portal_properties.mobile_properties.tracker_debug = True
        
        # Mobile tracking id string
        #self.MARKER = "http://www.google-analytics.com/__utm.gif"
        self.MARKER = '<img class="google-analytics"'
        
    def test_homepage_has_marker(self):
        """
        Test that we have tracker on home page.
        """
        
        self.setDiscriminateMode("mobile")
        self.browser.open(self.portal.absolute_url())
        self.assertTrue(self.MARKER in self.browser.contents)

    def test_subfolder(self):
        """ Test that we have a tracker on other pages than home.
        """

        self.loginAsPortalOwner()
        self.portal.invokeFactory("Folder", "folder")        
        
        # self.portal.portal_workflow.doActionFor(self.portal.folder, "submit")
        self.portal.portal_workflow.doActionFor(self.portal.folder, "publish")
        
        self.setDiscriminateMode("mobile")
                
        self.browser.open(self.portal.folder.absolute_url())
        self.assertTrue(self.MARKER in self.browser.contents)        

    def test_has_persistent_cookie(self):        
        """ Check that tracking by cookie works """ 
        
        self.setDiscriminateMode("mobile")
        self.browser.open(self.portal.absolute_url())        
        cookie = self.browser.headers["set-cookie"]
        # '__utmmobile="0xcef4dcf8945a222a"; Path=/; Expires=Thu, 12-Jan-2012 16:37:06 EET'
        cooky = cookie.split(";")[0]
        cooky = cooky.split('"')[1]
        #print "Got cooky:" + cooky

        # Now go there again        
        self.browser.open(self.portal.absolute_url())
        
        cooky2 = cookie.split(";")[0]
        cooky2 = cooky2.split('"')[1]
        #print "Got cooky 2:" + cooky
        
        self.assertEqual(cooky, cooky2)
        
    def test_query_string(self):
        """
        Test query string in tracked URL.
        """
        self.setDiscriminateMode("mobile")
        self.browser.open(self.portal.absolute_url() + "?set_lang=en")
        
        # TODO: Some smarter checks here, not
        # we check only that no exceptions are risen
        
TEST_HTML_1="""
<p>
<img src="foologo.jpg" />
</p>
"""

class TestDefaultTrackerFunctional(BaseTestCase):
    """ Test Plone web site tracker code in mobile.
    """ 

    def afterSetUp(self):
        
        BaseTestCase.afterSetUp(self)
        
        self.portal.portal_properties.mobile_properties.tracker_name = "plone-default"        
        self.MARKER = '<div id="analytics"'

    def test_homepage_has_marker(self):
        """
        Test that we have tracker on home page.
        """
        self.setDiscriminateMode("mobile")
        self.browser.open(self.portal.absolute_url())       
        self.assertTrue(self.MARKER in self.browser.contents)

        
class TestDocWithImage(BaseTestCase):
    """ Check that we transform document body text properly for mobile.
    """
 
    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)
        
        self.image_processor = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileImageProcessor) 
        self.image_processor.init()
        
        self.portal.invokeFactory("Document", "doc")
        self.doc = self.portal.doc
        
        self.loginAsAdmin()
        
    def test_no_transform(self):
        """
        Check there is no transform if not mobile.
        """
        self.browser.open(self.doc.absolute_url())
        self.assertTrue('src="logo.jpg"' in self.browser.contents)
   
    def test_relative(self):
        """
        Test relative image rewrite
        """ 
   
        self.setUA(MOBILE_USER_AGENT)
        self.doc.setText(TEST_HTML_1)   
   
        self.browser.open(self.doc.absolute_url())
        self.assertFalse('src="foologo.jpg"' in self.browser.contents)

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ThemeTestCase))
    suite.addTest(unittest.makeSuite(TestMobileOverrides))
    suite.addTest(unittest.makeSuite(TestPostPublication))
    suite.addTest(unittest.makeSuite(TestGAFunctional))
    suite.addTest(unittest.makeSuite(TestDefaultTrackerFunctional))
    return suite

