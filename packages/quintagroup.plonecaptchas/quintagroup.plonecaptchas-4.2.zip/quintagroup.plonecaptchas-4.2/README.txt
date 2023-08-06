Plone Captchas
==============

quintagroup.plonecaptchas is a simple captchas implementation for Plone, designed
for validation of human input in insecure forms. This is a standalone 
implementation which does not depend on captchas.net services.

quintagroup.plonecaptchas adds captcha support to Plone, it works together with 
quintagroup.captcha.core package (http://projects.quintagroup.com/products/wiki/quintagroup.captcha.core) and quintagroup.formlib.captcha (http://projects.quintagroup.com/products/wiki/quintagroup.formlib.captcha)

With these products installed captchas will be added to Plone's 'Send this', 
'Contact Us' (/contact-info) forms, and Plone's default discussion mechanism: 
'Add Comment' and 'Reply' forms.

quintagroup.plonecaptchas does not automatically plug to Plone's default registration
(/@@register). You can make captcha plug to Plone's Register form via Zope Management Interface.
Instructions here: http://projects.quintagroup.com/products/wiki/quintagroup.plonecaptchas#JoinForm

Requirements
------------

* Plone 4.0 and above 

Notes
-----

* For Plone 4 versions - use quintagroup.plonecaptchas 4.0 release and up http://plone.org/products/plone-captchas/releases/4.0. In your buildout.cfg file's egg section set product version::

   [buildout]
   ....
   eggs =
        ...
        quintagroup.plonecaptchas >=4.0

* For Plone 3 versions - use quintagroup.plonecaptcha 3.x releases http://plone.org/products/plone-captchas/releases/3.0. In your buildout.cfg file's egg section set product version::

   [buildout]
   ....
   eggs =
        ...
        quintagroup.plonecaptchas >=3.0,<4.0

* For Plone 2.x versions - use 1.3.4 version of qPloneCaptchas product for use on forms


Dependencies
------------

* quintagroup.captcha.core (PIL with _imagingft C module for dynamic captcha)
* quintagroup.formlib.captcha
* PIL with Jpeg and FreeType support

Plone Captchas on PloneFormGen forms 
------------------------------------

To make captchas work on forms created with PloneFormGen, please use 'quintagroup.pfg.captcha' product:
http://projects.quintagroup.com/products/wiki/quintagroup.pfg.captcha

Installation
------------

See docs/INSTALL.txt for instructions.

Note: If Plone Captchas is expected to be used with Plone Comments 
http://quintagroup.com/services/plone-development/products/plone-comments,
for proper behavior you have to install Plone Captchas first, and then Plone Comments.

Links
-----

* Plone Captchas home page - http://quintagroup.com/services/plone-development/products/plone-captchas
* Plone Captchas Screencasts - http://quintagroup.com/cms/screencasts/qplonecaptchas
* Documentation - http://projects.quintagroup.com/products/wiki/quintagroup.plonecaptchas
* SVN Repository - http://svn.quintagroup.com/products/quintagroup.plonecaptchas

Authors
-------

The product was developed by Quintagroup team:

* Andriy Mylenkyi 
* Volodymyr Cherepanyak
* Mykola Kharechko
* Vitaliy Stepanov
* Bohdan Koval

Contributors
------------

* Dorneles Tremea

Copyright (c) "Quintagroup": http://quintagroup.com, 2004-2011
