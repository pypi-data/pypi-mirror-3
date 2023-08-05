====================================
Google groups widgets for Django CMS
====================================

This extension provides the following plugins:

* *Google groups subscription*: wraps subscribe box into a Django CMS
   plugin, can be easily integrated into pages

Requirements
============

* `Django CMS >= 2.2 <http://django-cms.org>`_

Installation
============

If you want to use those plugins into your project, just follow this
procedure:

#. Open the *settings.py* file and add ``cmsplugin_googlegroups_widgets`` to the
   ``INSTALLED_APPS`` variable

#. Run the following command::

    $ ./manage.py syncb
