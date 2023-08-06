from Products.CMFCore import permissions as cmfcore_permissions

PROJECTNAME = "quintagroup.pfg.captcha"

ADD_PERMISSION = cmfcore_permissions.AddPortalContent

try:
    # Plone 4 and higher
    import plone.app.upgrade
    PLONE_VERSION = 4
    # for pyflakes test
    plone
except ImportError:
    PLONE_VERSION = 3
