GLOBALS = globals()
PRODUCT_NAME = 'quintagroup.plonecaptchas'
CAPTCHA_NAME = 'plonecaptchas'

HAS_APP_DISCUSSION = True
try:
    import plone.app.discussion
    plone.app.discussion  # keep pyflakes quiet
except ImportError:
    HAS_APP_DISCUSSION = False

#TOOL_ICON = 'tool.gif'
