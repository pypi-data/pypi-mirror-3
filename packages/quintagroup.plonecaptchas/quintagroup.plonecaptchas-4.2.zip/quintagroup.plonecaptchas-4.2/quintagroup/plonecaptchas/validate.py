from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import ICaptcha
from quintagroup.z3cform.captcha.validator import CaptchaValidator
from quintagroup.z3cform.captcha.widget import CaptchaWidget
from quintagroup.plonecaptchas.config import CAPTCHA_NAME
from quintagroup.plonecaptchas.interfaces import IQGDiscussionCaptchas

from zope.component import queryUtility
from zope.component import adapts
from zope.interface import Interface
from zope.schema.interfaces import IField
from plone.registry.interfaces import IRegistry
from z3c.form import validator


class QGDiscussionCaptchaValidator(CaptchaValidator):
    adapts(Interface, IQGDiscussionCaptchas, Interface, IField, Interface)

    def validate(self, value):

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        if settings.captcha == CAPTCHA_NAME:
            super(QGDiscussionCaptchaValidator, self).validate(value)


validator.WidgetValidatorDiscriminators(QGDiscussionCaptchaValidator,
                                        widget=CaptchaWidget,
                                        field=ICaptcha['captcha'])
