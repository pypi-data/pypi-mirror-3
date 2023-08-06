from plone.app.discussion.browser.captcha import CaptchaExtender
from quintagroup.z3cform.captcha.widget import CaptchaWidgetFactory
from plone.app.discussion import vocabularies
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import interfaces
from quintagroup.plonecaptchas.config import CAPTCHA_NAME
from quintagroup.plonecaptchas.interfaces import IQGDiscussionCaptchas
from zope.interface import Interface
from zope.component import adapts
from plone.app.discussion.browser.comments import CommentForm


class CaptchaExtender(CaptchaExtender):
    adapts(Interface, IQGDiscussionCaptchas, CommentForm)

    def update(self):
        super(CaptchaExtender, self).update()
        if self.captcha == CAPTCHA_NAME and self.isAnon:
            self.form.fields['captcha'].widgetFactory = CaptchaWidgetFactory
            if self.form.fields['captcha'].mode == interfaces.HIDDEN_MODE:
                self.form.fields['captcha'].mode = None


def captcha_vocabulary(context):
    """ Extend captcha vocabulary with quintagroup.plonecaptchas"""
    terms = vocabularies.captcha_vocabulary(context)._terms
    terms.append(SimpleTerm(value=CAPTCHA_NAME,
                            token=CAPTCHA_NAME,
                            title=CAPTCHA_NAME))
    return SimpleVocabulary(terms)
