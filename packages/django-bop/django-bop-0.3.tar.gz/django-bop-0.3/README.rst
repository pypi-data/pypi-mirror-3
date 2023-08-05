==========
django-bop
==========

Django-bop provides Basic Object-level Permissions for django 1.2 and
later. It is based on the django-advent article_ 'Object Permissions'
by Florian Apolloner.

Although there are a few other_ permission backends I wanted a
simple(r) backend that closely matches the existing django
functionality.

Features
--------

Django-bop provides several mechanisms to manage and check the
permissions for objects:

* bop.admin.ObjectAdmin
* bop.forms.inline_permissions_form_factory
* api.grant and api.revoke
* bop.backends.ObjectBackend
* ifhasperm templatetag
* bop.managers.UserObjectManager 
* bop.managers.ObjectPermissionManager

Also of interest:

* has_model_perms

Installation
------------

Install it in your (virtual) environment::

  $ pip install django-bop

If you haven't already you should also install south::

  $ pip install South

Add 'bop' (and south) to you INSTALLED_APPS in settings.py::

  INSTALLED_APPS = (
    ...
    'south',
    'bop',
  )

While in settings.py specify the AUTHENTICATION_BACKENDS::

  AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'bop.backends.ObjectBackend',
  )

If you, optionally, want to give permissions to anonymous users you
should do the following:

1. Add a user to contrib.auth.models.User to represent anonymous users
   (e.g. via the admin). Give it an appropriate name (anon /
   anonymous) so it easily recognized when assigning permissions.

2. Add ANONYMOUS_USER_ID to settings.py::

     ANONYMOUS_USER_ID = 2

If, in addition -- and again optionally -- you want to support
Model-permissions for anonymous users, you can add the
AnonymousModelBackend::

  AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.ModelBackend',
      'bop.backends.AnonymousModelBackend',
      'bop.backends.ObjectBackend',
  )

When all configuration is done, bring the database up to date::

  $ ./manage.py migrate bop


.. _article: http://djangoadvent.com/1.2/object-permissions/
.. _other: http://www.djangopackages.com/grids/g/perms/
