import unittest
from quintagroup.pfg.captcha.field import CAPTCHA_ID
from quintagroup.pfg.captcha.tests.base import TestCaseNotInstalled, \
    REQUIREMENTS


class TestMigration(TestCaseNotInstalled):
    """Migration perform recreation old CaptchaField
    objects from qPloneCaptchaField product to new
    CaptchaField from quintagroup.pfg.captcha package.

    Migration based on:
      * presence old portal type CaptchaField with
        "qPloneCaptchaField" value in *product* field.
      * presence of CaptchaField objects on the site.

    This TestCase emulate migration with:
      1. Install new quintagroup.pfg.captcha package
         and add test CaptchaField object.
      2. Change *product" field value in
         portal_tyeps/CaptchaField FTI
    Then it install quintagroup.pfg.captcha and test if
    tested CaptchaField object is recreated and *product*
    field for portal_type/CaptchaField is changed to
    quintagroup.pfg.captcha.
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.qi = self.portal.portal_quickinstaller
        self.pt = self.portal.portal_types
        self.prepareToMigration()

    def beforeTearDown(self):
        self.qi.uninstallProducts(["quintagroup.pfg.captcha", ])

    def prepareToMigration(self):
        # Install types
        for p in REQUIREMENTS:
            if not self.qi.isProductInstalled(p):
                self.qi.installProduct(p)
        # Add captcha field
        self.portal.invokeFactory("FormFolder", 'test_form')
        test_form = self.portal['test_form']
        test_form.invokeFactory("CaptchaField", CAPTCHA_ID)
        self.cf_path = "test_form/key"
        self.old_cf = self.portal.unrestrictedTraverse(self.cf_path)
        self.assert_(self.old_cf)
        self.pt['CaptchaField'].manage_changeProperties(
            product="qPloneCaptchaField")
        self.qi.manage_delObjects('quintagroup.pfg.captcha')

    def testMigration(self):
        self.addProduct("quintagroup.pfg.captcha")
        new_cf = self.portal.unrestrictedTraverse(self.cf_path)
        self.assert_(self.old_cf != new_cf)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMigration))
    return suite
