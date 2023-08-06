import transaction

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import setup as ptc_setup
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from quintagroup.plonecaptchas.config import PRODUCT_NAME

# TESTING CONSTANTS
CAPTCHA_KEY = 'captcha_key'
CAPTCHAS_COUNT = 165
LAYERS = ['captchas_discussion', 'captchas_sendto_form',
          'captchas_contact_info']

TOOL_ICON = 'skins/plone_captchas/tool.gif'
TOOL_ID = 'portal_captchas'
CONFIGLET_ID = "qpc_tool"
PROPERTY_SHEET = 'qPloneCaptchas'

# register_form profile
RF_PROFILE = 'profile-quintagroup.plonecaptchas:register_form'

ptc.setupPloneSite()


class NotInstalled(PloneSite):
    """ Only package register, without installation into portal
    """

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import quintagroup.captcha.core
        import quintagroup.plonecaptchas
        zcml.load_config('configure.zcml', quintagroup.captcha.core)
        zcml.load_config('configure.zcml', quintagroup.plonecaptchas)
        fiveconfigure.debug_mode = False
        ztc.installPackage('quintagroup.captcha.core')
        ztc.installPackage('quintagroup.plonecaptchas')


class Installed(NotInstalled):
    """ Install product into the portal
    """
    @classmethod
    def setUp(cls):
        app = ztc.app()
        portal = app[ptc_setup.portal_name]

        # Sets the local site/manager
        ptc_setup._placefulSetUp(portal)
        # Install PROJECT
        qi = getattr(portal, 'portal_quickinstaller', None)
        qi.installProduct(PRODUCT_NAME)

        # Run register_form profile
        gs = getattr(portal, 'portal_setup', None)
        gs.runAllImportStepsFromProfile(RF_PROFILE)

        transaction.commit()

    @classmethod
    def tearDown(cls):
        ptc_setup._placefulTearDown()


class TestCase(ptc.PloneTestCase):
    layer = Installed


class TestCaseNotInstalled(ptc.PloneTestCase):
    layer = NotInstalled


class FunctionalTestCase(ptc.FunctionalTestCase):
    layer = Installed


class FunctionalTestCaseNotInstalled(ptc.FunctionalTestCase):
    layer = NotInstalled
