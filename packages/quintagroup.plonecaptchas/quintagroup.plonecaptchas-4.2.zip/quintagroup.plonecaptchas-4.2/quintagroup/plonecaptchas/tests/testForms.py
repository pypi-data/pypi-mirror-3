import unittest
import doctest
import re
from urllib import urlencode
from StringIO import StringIO

from Products.PloneTestCase.PloneTestCase import portal_owner
from Products.PloneTestCase.PloneTestCase import default_password

from quintagroup.plonecaptchas.tests.base import FunctionalTestCase, ztc
from quintagroup.plonecaptchas.config import PRODUCT_NAME, HAS_APP_DISCUSSION

from quintagroup.captcha.core.tests.testWidget import IMAGE_PATT, NOT_VALID
from quintagroup.captcha.core.tests.testWidget import addTestLayer
from quintagroup.captcha.core.tests.base import testPatch
from quintagroup.captcha.core.utils import getWord, decrypt, parseKey

from plone.app.controlpanel.security import ISecuritySchema

# BBB for plone v<3.1, where plone.protect not used yet
PROTECT_SUPPORT = True
try:
    from plone import protect
    # pyflakes fix (pyflakes message: 'protect' imported but unused)
    protect
except ImportError:
    PROTECT_SUPPORT = False

# USE PATCH FROM quintagroup.captcha.core
# patch to use test images and dictionary
testPatch()


class TestFormMixin(FunctionalTestCase):

    formkey_key = "key"
    formkey_hashkey = "hashkey"

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.addProduct(PRODUCT_NAME)
        # Add test_captcha layer from quintagroup.captcah.core
        addTestLayer(self)
        # Prepare form data
        self.basic_auth = ':'.join((portal_owner, default_password))
        self.form_url = ''
        self.form_method = "POST"
        self.hasAuthenticator = False
        self.form_data = self.getFormData()
        # Prepare captcha related test data
        self.captcha_key = self.portal.captcha_key
        self.hashkey = self.portal.getCaptcha()
        self.form_data[self.formkey_hashkey] = self.hashkey
        self.form_data[self.formkey_key] = ''

    def getFormData(self):
        raise NotImplementedError(
            "getFormData not implemented")

    def publishForm(self):
        stdin_data = None
        form_url = self.portal.absolute_url(1) + self.form_url
        # Prepare form data
        if PROTECT_SUPPORT and self.hasAuthenticator:
            self.form_data['_authenticator'] = self._getauth()
        form_data = urlencode(self.form_data)
        if self.form_method.upper() == 'GET':
            form_url += "?%s" % form_data
        else:
            stdin_data = StringIO(form_data)
        # Publish form and get response
        response = self.publish(form_url, self.basic_auth,
            request_method=self.form_method, stdin=stdin_data)
        return response

    def _getauth(self):
        # Fix authenticator for the form
        authenticator = self.portal.restrictedTraverse("@@authenticator")
        html = authenticator.authenticator()
        handle = re.search('value="(.*)"', html).groups()[0]
        return handle

    def elog(self, name="", response=""):
        open("/tmp/test.%s.html" % name, "w").write(response)
        logs = self.portal.error_log.getLogEntries()
        if len(logs) > 0:
            i = 0
            while logs:
                l = logs.pop()
                i += 1
                open("/tmp/test.%s.error.%d.html" % (l["id"], i),
                                                     "w").write(l["tb_html"])

    def testImage(self):
        self.form_data = {}
        self.form_method = "GET"
        response = self.publishForm().getBody()
        patt = re.compile(IMAGE_PATT % self.portal.absolute_url())
        match_obj = patt.search(response)
        self.elog("image", response)
        img_url = match_obj.group(1)

        content_type = self.publish(
                            '/plone' + img_url).getHeader('content-type')
        self.assertTrue(content_type.startswith('image'),
            "Wrong captcha image content type")

    def testSubmitRightCaptcha(self):
        key = getWord(int(parseKey(decrypt(self.captcha_key,
                                           self.hashkey))['key']) - 1)
        self.form_data[self.formkey_key] = key

        response = self.publishForm().getBody()
        self.elog("right", response)
        self.assertFalse(NOT_VALID.search(response))

    def testSubmitWrongCaptcha(self):
        self.form_data[self.formkey_key] = 'wrong word'
        response = self.publishForm().getBody()
        self.elog("wrong", response)
        self.assertTrue(NOT_VALID.search(response))

    def testSubmitRightCaptchaTwice(self):
        key = getWord(int(parseKey(decrypt(self.captcha_key,
                                           self.hashkey))['key']) - 1)
        self.form_data[self.formkey_key] = key

        response1 = self.publishForm().getBody()
        self.elog("right1", response1)
        response2 = self.publishForm().getBody()
        self.elog("right2", response2)
        self.assertTrue(NOT_VALID.search(response2))


class TestDiscussionForm(TestFormMixin):

    def afterSetUp(self):
        TestFormMixin.afterSetUp(self)
        self.portal.invokeFactory('Document', 'index_html')
        self.portal['index_html'].allowDiscussion(True)
        self.form_url = '/index_html/discussion_reply_form'

    def getFormData(self):
        return {'form.submitted': '1',
                'subject': 'testing',
                'Creator': portal_owner,
                'body_text': 'Text in Comment',
                'discussion_reply:method': 'Save',
                'form.button.form_submit': 'Save'}


class TestRegisterForm(TestFormMixin):

    formkey_key = "form.captcha"
    formkey_hashkey = "form..hashkey"

    def afterSetUp(self):
        TestFormMixin.afterSetUp(self)
        ISecuritySchema(self.portal).enable_self_reg = True
        self.portal._updateProperty('validate_email', False)
        self.hasAuthenticator = True
        self.form_url = '/@@register'
        self.basic_auth = ":"
        self.logout()

    def getFormData(self):
        return {"form.fullname": "Tester",
                "form.username": "tester",
                "form.email": "tester@test.com",
                "form.password": "123456",
                "form.password_ctl": "123456",
                'form.actions.register': 'Register'}


class TestSendtoForm(TestFormMixin):

    def afterSetUp(self):
        TestFormMixin.afterSetUp(self)
        self.portal.invokeFactory('Document', 'index_html')
        self.portal['index_html'].allowDiscussion(True)
        self.form_url = '/index_html/sendto_form'

    def getFormData(self):
        return {'form.submitted': '1',
                "send_to_address": "recipient@test.com",
                "send_from_address": "sender@test.com",
                'comment': 'Text in Comment',
                'form.button.Send': 'Save'}


def send_patch(self, *args, **kwargs):
    """This patch prevent breakage on sending."""


class TestContactInfo(TestFormMixin):

    def afterSetUp(self):
        TestFormMixin.afterSetUp(self)
        # preparation to form correct working
        self.portal._updateProperty('email_from_address', 'manager@test.com')
        self.logout()
        self.form_url = '/contact-info'
        self.orig_mh_send = self.portal.MailHost.send
        self.portal.MailHost.send = send_patch

    def beforeTearDown(self):
        self.portal.MailHost.send = self.orig_mh_send

    def getFormData(self):
        return {'form.submitted': '1',
                "sender_fullname": "tester",
                "sender_from_address": "sender@test.com",
                'subject': 'Subject',
                'message': 'Message',
                'form.button.Send': 'Save'}


def test_suite():
    suite = unittest.TestSuite()
    if HAS_APP_DISCUSSION:
        suite.addTest(unittest.TestSuite([
            ztc.FunctionalDocFileSuite(
                'discussion.txt', package='quintagroup.plonecaptchas.tests',
                test_class=FunctionalTestCase, globs=globals(),
                optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                    doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            ]))

    else:
        suite.addTest(unittest.makeSuite(TestDiscussionForm))
    suite.addTest(unittest.makeSuite(TestRegisterForm))
    suite.addTest(unittest.makeSuite(TestSendtoForm))
    suite.addTest(unittest.makeSuite(TestContactInfo))
    return suite
