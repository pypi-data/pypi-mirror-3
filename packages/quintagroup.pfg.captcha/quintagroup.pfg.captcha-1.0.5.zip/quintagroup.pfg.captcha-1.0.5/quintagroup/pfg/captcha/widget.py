from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Registry import registerWidget

CAPTCHA_MACRO = "captchaField_widget"


class CaptchaWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({'macro': CAPTCHA_MACRO})


registerWidget(CaptchaWidget,
               title='Captcha widget',
               description=('Renders captcha image and string input',),
               used_for=('quintagroup.pfg.captcha.field.CaptchaField',)
              )
