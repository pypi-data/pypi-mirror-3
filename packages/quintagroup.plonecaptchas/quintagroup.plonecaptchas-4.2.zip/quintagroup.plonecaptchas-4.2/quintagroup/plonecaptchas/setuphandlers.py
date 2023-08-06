import logging
from zope.component import getSiteManager

logger = logging.getLogger('quintagroup.plonecaptchas')


def registerDiscussionLayer(context):
    """ Register browser layer for extending discussion
        with quintagroup captcha
    """
    from quintagroup.plonecaptchas.interfaces import IQGDiscussionCaptchas
    from plone.browserlayer.utils import register_layer
    name = "QGCaptchaDiscussionLayer"
    site = getSiteManager(context)
    register_layer(IQGDiscussionCaptchas, name, site_manager=site)


def removeBrowserLayers(site):
    """ Remove browser layers.
    """
    from plone.browserlayer.utils import unregister_layer
    from plone.browserlayer.interfaces import ILocalBrowserLayerType

    layers = ["quintagroup.plonecaptchas", "QGCapchaDiscussionLayer"]
    site = getSiteManager(site)
    registeredLayers = [r.name for r in site.registeredUtilities()
                        if r.provided == ILocalBrowserLayerType]
    for name in layers:
        if name in registeredLayers:
            unregister_layer(name, site_manager=site)
            logger.log(logging.INFO,
                       "Unregistered \"%s\" browser layer." % name)


def uninstall(context):
    """ Do customized uninstallation.
    """
    if context.readDataFile('qgplonecaptchas_uninstall.txt') is None:
        return
    site = context.getSite()
    removeBrowserLayers(site)
