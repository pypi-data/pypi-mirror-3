Introduction
============

Quintagroup PloneFormGen Captcha Field (quintagroup.pfg.captcha) allows to 
add captcha field to PloneFormGen forms.


Usage
-----

To add captcha to PloneFormGen forms you need to install 2 Plone products:

* PloneFormGen - for creating the form itself
* Quintagroup PloneFormGen CaptchaField - for adding captcha field to the form, it will be installed together with Quintagroup Captcha Core (quintagroup.captcha.core) package that enables Plone captchas on Plone sites.

Make sure you install PloneFormGen first, otherwise quintagroup.pfg.captcha may fail to work correctly.

quintagroup.pfg.captcha plugs to PloneFormGen forms, so after successful installation
you will have a new field among fields available for PloneFormGen form - Captcha Field. 
Everything you need to do is to select this field from 'Add..' drop-down menu and save it.


Supported Plone versions
------------------------

* 3.x
* 4.0

Links
-----
    
* Documentation - http://projects.quintagroup.com/products/wiki/quintagroup.pfg.captcha
* SVN Repository - http://svn.quintagroup.com/products/quintagroup.pfg.captcha


Notes
-----

* If you want to change captcha look - use quintagroup.captcha.core settings: http://projects.quintagroup.com/products/wiki/quintagroup.captcha.core

* If you want captcha for Plone default forms - use quintagroup.plonecaptchas product http://projects.quintagroup.com/products/wiki/quintagroup.plonecaptchas

* Migration from qPloneCaptchaField: just replace old Products.qPloneCaptchaField with
  quintagroup.pfg.captcha in the buildout and install new package with quickinstaller -
  it will replace all old ones captcha fields (qPloneCaptchaField's) with new one.


Authors
-------

The product is developed by Quintagroup.com team:

* Volodymyr Cherepanyak
* Taras Melnychuk
* Andriy Mylenkyi
* Vitaliy Stepanov

Copyright (c) "Quintagroup": http://quintagroup.com, 2004-2010

