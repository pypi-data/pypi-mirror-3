from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from Products.CMFCore.permissions import View

from Products.Archetypes.atapi import StringField
from Products.ATContentTypes.content.base import registerATCT

from Products.PloneFormGen.content.fields import FGStringField
from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.content.fieldsBase \
        import BaseFieldSchemaStringDefault

from quintagroup.pfg.captcha.config import PROJECTNAME
from quintagroup.pfg.captcha.widget import CaptchaWidget

CAPTCHA_ID = 'key'
HIDDEN_FIELDS = [
    'title',
    'description',
    'required',
    'hidden',
    'fgTDefault',
    'fgTEnabled',
    'fgDefault',
    'fgTValidator']


def finalizeCaptchaFieldSchema(schema):
    schema['title'].default = 'key'
    for field in HIDDEN_FIELDS:
        schema[field].widget.visible = {'view': 'invisible',
                                        'edit': 'invisible'}

CaptchaFieldSchema = BaseFieldSchemaStringDefault.copy()
finalizeCaptchaFieldSchema(CaptchaFieldSchema)


def addCaptchaField(self, id, **kwargs):
    obj = CaptchaField(id)
    notify(ObjectCreatedEvent(obj))
    self._setObject(id, obj)
    obj = self._getOb(id)
    obj.initializeArchetype(**kwargs)
    notify(ObjectModifiedEvent(obj))
    return obj.getId()


class CaptchaField(FGStringField):

    _at_rename_after_creation = True
    schema = CaptchaFieldSchema

    def __init__(self, oid, **kwargs):
        """ initialize class """
        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringField('fg_string_field',
            searchable=0,
            required=1,
            write_permission=View,
            validators=('isCaptchaCorrect',),
            widget=CaptchaWidget(),
            )

registerATCT(CaptchaField, PROJECTNAME)
