from plone.theme.interfaces import IDefaultPloneLayer
from quintagroup.plonecaptchas.config import HAS_APP_DISCUSSION

if HAS_APP_DISCUSSION:
    from zope.publisher.interfaces.browser import IDefaultBrowserLayer

    class IQGDiscussionCaptchas(IDefaultBrowserLayer):
        """ quintagroup.plonecaptchas browser layer interface for
            plone.app.discussion
        """


class IQGPloneCaptchas(IDefaultPloneLayer):
    """ quintagroup.plonecaptchas browser layer interface """
