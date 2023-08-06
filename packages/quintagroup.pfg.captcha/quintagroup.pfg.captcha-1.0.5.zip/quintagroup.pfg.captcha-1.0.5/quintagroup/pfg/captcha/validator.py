from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator

from quintagroup.pfg.captcha.config import PLONE_VERSION


class CaptchaValidator:

    name = 'CaptchaValidator'
    title = ""
    description = ""

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        form = kwargs.get('instance')
        portal = getToolByName(form, 'portal_url').getPortalObject()
        result = portal.captcha_validator()
        if result.status == 'failure':
            return ("%(problem)s" % {'problem': result.errors['key'][0]})
        else:
            return 1

if PLONE_VERSION == 4:
    from zope.interface import classImplements
    classImplements(CaptchaValidator, IValidator)
else:
    CaptchaValidator.__implements__ = (IValidator,)

validation.register(CaptchaValidator('isCaptchaCorrect'))
