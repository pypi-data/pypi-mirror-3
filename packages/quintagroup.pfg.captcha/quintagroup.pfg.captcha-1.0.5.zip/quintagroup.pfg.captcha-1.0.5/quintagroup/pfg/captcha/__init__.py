from Products.CMFCore import utils
from Products.Archetypes.atapi import process_types, listTypes

from quintagroup.pfg.captcha.config import PROJECTNAME
from quintagroup.pfg.captcha.config import ADD_PERMISSION

from quintagroup.pfg.captcha.field import CaptchaField
from quintagroup.pfg.captcha.widget import CaptchaWidget
from quintagroup.pfg.captcha.validator import CaptchaValidator
#for pyflakes test
CaptchaField
CaptchaWidget
CaptchaValidator


def initialize(context):

    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                      PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types=content_types,
        permission=ADD_PERMISSION,
        extra_constructors=constructors,
        fti=ftis,
        ).initialize(context)
