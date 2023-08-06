import transaction

from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase import setup as ptc_setup
from Products.PloneTestCase import PloneTestCase as ptc

PACKAGES = [
    'quintagroup.captcha.core',
    'quintagroup.pfg.captcha',
]
REQUIREMENTS = ['PloneFormGen', ] + PACKAGES

ptc.setupPloneSite()

# !!! Not initialized factory methods for the content types
# !!! (for Plone-4+) if located in NotInstalled.setUp
# !!! method of the layer class.
ztc.installProduct('PloneFormGen')


class NotInstalled(PloneSite):
    """ Only package register, without installation into portal
    """
    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import quintagroup.pfg.captcha
        zcml.load_config('configure.zcml', quintagroup.pfg.captcha)
        fiveconfigure.debug_mode = False
        ztc.installPackage('quintagroup.pfg.captcha')
        ztc.installPackage('quintagroup.captcha.core')

    @classmethod
    def tearDown(cls):
        ptc_setup.cleanupPloneSite(ptc_setup.portal_name)


class Installed(NotInstalled):
    """ Install product into the portal
    """
    @classmethod
    def setUp(cls):
        app = ztc.app()
        portal = app[ptc_setup.portal_name]

        # Sets the local site/manager
        ptc_setup._placefulSetUp(portal)
        # Install PROJECT
        qi = getattr(portal, 'portal_quickinstaller', None)
        for p in REQUIREMENTS:
            if not qi.isProductInstalled(p):
                qi.installProduct(p)
        transaction.commit()

    @classmethod
    def tearDown(cls):
        ptc_setup._placefulTearDown()


class TestCase(ptc.PloneTestCase):
    layer = Installed


class TestCaseNotInstalled(ptc.PloneTestCase):
    layer = NotInstalled
