from zope.i18nmessageid import MessageFactory

from AccessControl import ModuleSecurityInfo

product = 'quintagroup.plonecaptchas'
ProductMessageFactory = MessageFactory(product)
ModuleSecurityInfo(product).declarePublic("ProductMessageFactory")

#from quintagroup.plonecaptchas import config
#allow_module('quintagroup.plonecaptchas.config')


def initialize(context):
    pass
