import logging
from zope.component import queryMultiAdapter

logger = logging.getLogger('quintagroup.pfg.captcha')

captcha_fields = []


def migrateToPackage(context):
    """
    Collect old Products.qPloneCaptchaFields fields (before types tool setup).
    """
    global captcha_fields
    if context.readDataFile('quintagroup.pfg.captcha_default.txt') is None:
        return

    site = context.getSite()
    plone_tools = queryMultiAdapter((site, site.REQUEST), name="plone_tools")
    ptypes = plone_tools.types()
    cftype = getattr(ptypes, 'CaptchaField', None)
    if cftype and getattr(cftype, 'product', "") == "qPloneCaptchaField":
        catalog = plone_tools.catalog()
        captcha_fields = [(cf.id, cf.getObject().aq_parent) \
                          for cf in catalog.search(
                                {'portal_type': 'CaptchaField'})]
        logger.info("Old Products.qPloneCaptchaField fields collected.")


def afterTypesTool(context):
    """ Replace old qPloneCaptchaField with new quintagroup.pfg.captcha fields
    (after types tool setup).
    """
    global captcha_fields

    if context.readDataFile('quintagroup.pfg.captcha_default.txt') is None:
        return

    while captcha_fields:
        cf_id, form = captcha_fields.pop()
        form.manage_delObjects(cf_id)
        form.invokeFactory("CaptchaField", cf_id)
        logger.info("Fixed CaptchaField in '%s'" % form.getId())
    logger.info("Finish Captcha field fixing")
