import string
import unittest

from Products.CMFCore.permissions import View
from Products.Archetypes.atapi import StringField
from Products.Archetypes.Registry import availableWidgets
from Products.validation import validation

from quintagroup.pfg.captcha import CaptchaField
from quintagroup.pfg.captcha import CaptchaWidget
from quintagroup.pfg.captcha import CaptchaValidator
from quintagroup.pfg.captcha.widget import CAPTCHA_MACRO
from quintagroup.pfg.captcha.field import CAPTCHA_ID, HIDDEN_FIELDS
from quintagroup.pfg.captcha.tests.base import TestCase, REQUIREMENTS

_marker = object()


class TestInstallations(TestCase):

    def testInstalledProducts(self):
        qi = self.portal.portal_quickinstaller
        installed = [p['id'] for p in qi.listInstalledProducts()]
        for p in REQUIREMENTS:
            if p.startswith('Products'):
                p = p[9:]
            self.assertEqual(p in installed, True,
                '"%s" product not installed' % p)

    def testType(self):
        pt = self.portal.portal_types
        self.assertEqual("CaptchaField" in pt.objectIds(), True)

    def testPortalFactory(self):
        pf = self.portal.portal_factory
        self.assertEqual("CaptchaField" in pf.getFactoryTypes(), True)

    def testWorkflow(self):
        pw = self.portal.portal_workflow
        default_chain = pw.getDefaultChain()
        cf_chain = pw.getChainForPortalType('CaptchaField')
        self.assertNotEqual(cf_chain == default_chain, True)

    def testNotToList(self):
        navtree = self.portal.portal_properties.navtree_properties
        mtNotToList = navtree.getProperty("metaTypesNotToList")
        self.assertEqual('CaptchaField' in mtNotToList, True)

    def testSkins(self):
        ps = self.portal.portal_skins
        self.assertEqual("qplonecaptchafield" in ps.objectIds(), True)
        for sname, spath in ps.getSkinPaths():
            paths = filter(None, map(string.strip, spath.split(',')))
            self.assertEqual("qplonecaptchafield" in paths, True,
                '"qplonecaptchafield" layer not present in "%s" skin' % sname)


class TestCaptchaField(TestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.invokeFactory('CaptchaField', CAPTCHA_ID)

    def testSchema(self):
        cf = getattr(self.ff1, CAPTCHA_ID)
        schema = cf.Schema()
        for field in HIDDEN_FIELDS:
            visibility = schema[field].widget.visible
            self.assertEqual(visibility, {'view': 'invisible',
                                          'edit': 'invisible'},
                '"%s" field is not hidden, but %s:' % (field, visibility))

    def testFGField(self):
        cf = getattr(self.ff1, CAPTCHA_ID)
        fgField = getattr(cf, 'fgField', _marker)
        self.assertNotEqual(fgField, _marker)
        # Test fgField properties
        self.assertEqual(type(fgField), StringField)
        self.assertEqual(bool(fgField.searchable), False)
        self.assertEqual(fgField.write_permission, View)
        self.assertEqual(type(fgField.widget), CaptchaWidget)
        validators = [v.__class__ for v in fgField.validators._chain]
        self.assertEqual(CaptchaValidator in validators, True)


class TestCaptchaWidget(TestCase):

    CF = CaptchaField.__module__ + '.CaptchaField'
    CW = CaptchaWidget.__module__ + '.CaptchaWidget'

    def afterSetUp(self):
        self.widgets = dict(availableWidgets())

    def testRegistration(self):
        self.assertEqual(self.CW in self.widgets, True)
        cw = self.widgets[self.CW]
        self.assertEqual(self.CF in cw.used_for, True)

    def testWidgetMacro(self):
        widget_macro = self.widgets[self.CW].klass._properties['macro']
        self.assertEqual(widget_macro, CAPTCHA_MACRO)

    def testWidgetMacroAccessable(self):
        macro = self.portal.restrictedTraverse(CAPTCHA_MACRO)
        self.assertNotEqual(macro, None)


class TestCaptchaValidator(TestCase):

    def getValidator(self):
        return validation.validatorFor('isCaptchaCorrect')

    def testRegistration(self):
        self.assertEqual(self.getValidator().__class__, CaptchaValidator)

    def patchCoreValidator(self, status, error=""):
        # Patch quintagroup.catpcha.core' captcha_validator
        class MockState:
            def __init__(self, status, error=""):
                self.status = status
                self.errors = {'key': [error, ]}

        patch_validator = lambda: MockState(status, error)
        self.portal.captcha_validator = patch_validator

    def testValidationSuccess(self):
        # PFG validator must call patched quintagroup.captcha.core'
        # captcha_validator and successfully validate the data.
        validator = self.getValidator()
        self.patchCoreValidator("success")
        result = validator('test', instance=self.portal)
        self.assertEqual(result, 1)

    def testValidationFailure(self):
        # PFG validator must call patched quintagroup.captcha.core'
        # captcha_validator and return error.
        validator = self.getValidator()
        self.patchCoreValidator("failure", "Wrong value")
        result = validator('test', instance=self.portal)
        self.assertEqual(result, "Wrong value")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstallations))
    suite.addTest(unittest.makeSuite(TestCaptchaField))
    suite.addTest(unittest.makeSuite(TestCaptchaWidget))
    suite.addTest(unittest.makeSuite(TestCaptchaValidator))
    return suite
