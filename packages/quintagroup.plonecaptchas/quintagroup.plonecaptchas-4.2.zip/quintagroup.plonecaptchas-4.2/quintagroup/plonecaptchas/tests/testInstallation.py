import unittest
from quintagroup.plonecaptchas.tests.base import TestCase, LAYERS

from Products.CMFCore.utils import getToolByName

from zope.interface import alsoProvides
from zope.component import getSiteManager
from zope.component import queryMultiAdapter
from plone.browserlayer.interfaces import ILocalBrowserLayerType

from quintagroup.plonecaptchas.interfaces import IQGPloneCaptchas
from quintagroup.plonecaptchas.browser.register import CaptchaRegistrationForm
from quintagroup.plonecaptchas.config import PRODUCT_NAME


class TestInstallation(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.skins = getToolByName(self.portal, 'portal_skins', None)

    def testSkinInstall(self):
        for skin in self.skins.getSkinSelections():
            path = self.skins.getSkinPath(skin)
            path = map(str.strip, path.split(','))
            for layer in LAYERS:
                self.assert_(layer.split('/')[0] in self.skins.objectIds(),
                             '%s directory view not found in portal_skins '\
                             'after installation' % layer)
                self.assert_(layer in path,
                             '%s layer not found in %s' % (PRODUCT_NAME, skin))

    def testBrowserLayerRegistration(self):
        # Test if IQGPloneCaptchas browser layer registered on installation
        site = getSiteManager(self.portal)
        registeredLayers = [r.name for r in site.registeredUtilities()
                            if r.provided == ILocalBrowserLayerType]
        self.assertEqual("quintagroup.plonecaptchas" in registeredLayers, True)

    def testRegisterFormOverriden(self):
        # Mark request with IQGPloneCaptchas browser layer interface
        alsoProvides(self.portal.REQUEST, IQGPloneCaptchas)
        register = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                     name="register")
        self.assertEqual(isinstance(register, CaptchaRegistrationForm), True)


class TestUninstallation(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.skins = getToolByName(self.portal, 'portal_skins', None)
        self.qi = getToolByName(self.portal, 'portal_quickinstaller', None)
        self.qi.uninstallProducts([PRODUCT_NAME])

    def testProductUninstalled(self):
        self.assertNotEqual(self.qi.isProductInstalled(PRODUCT_NAME), True)

    def testSkinUninstall(self):
        for skin in self.skins.getSkinSelections():
            path = self.skins.getSkinPath(skin)
            path = map(str.strip, path.split(','))
            for layer in LAYERS:
                self.assertTrue(
                        not layer.split('/')[0] in self.skins.objectIds(),
                        '%s directory view found in portal_skins '\
                        'after uninstallation' % layer)
                self.assert_(not layer in path,
                    '%s layer found in %s skin after uninstallation' % (layer,
                                                                        skin))

    def testBrowserLayerUnregistration(self):
        # Test if IQGPloneCaptchas browser layer registered on installation
        site = getSiteManager(self.portal)
        registeredLayers = [r.name for r in site.registeredUtilities()
                            if r.provided == ILocalBrowserLayerType]
        self.assertNotEqual("quintagroup.plonecaptchas" in registeredLayers,
                            True)

    def testRegisterFormOverriden(self):
        # Mark request with IQGPloneCaptchas browser layer interface
        register = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                     name="register")
        self.assertNotEqual(isinstance(register, CaptchaRegistrationForm),
                            True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstallation))
    suite.addTest(unittest.makeSuite(TestUninstallation))
    return suite
