===================================
Viadeo resume plugin for Django CMS
===================================

This plugin lets you display a resume using your `Viadeo
<http://www.viadeo.com>`_ profile.

Requirements
============

* `Django CMS >= 2.2 <http://django-cms.org>`_
* `oauth2 python module <https://github.com/simplegeo/python-oauth2>`_
* `simplejson python module <https://github.com/simplejson/simplejson>`_

Installation
============

To use this plugin into your project, just follow this procedure:

#. Open the *settings.py* file and add ``cmsplugin_viadeo_resume`` to the
   ``INSTALLED_APPS`` variable

#. Define the following variables into your config file::

    VIADEO_CLIENT_ID = "<your client ID>"
    VIADEO_CLIENT_SECRET = "<your client secret>"
    VIADEO_ACCESS_TOKEN = "<your access token>"

Read the `Viadeo documentation
<http://dev.viadeo.com/documentation/authentication/request-an-api-key/>`_
to learn how to request an API key.
