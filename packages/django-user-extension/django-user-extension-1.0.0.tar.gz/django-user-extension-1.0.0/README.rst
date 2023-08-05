=====================
Django-User-Extension
=====================


Description
===========

This is a simple app that that helps you subclass the Django User model. It
makes use of the InheritanceQuerySet provided by `Django-Model-Utils`_ to make
it possible for you to create as many subclasses of the User model as you like.

It's usually recommended to create a "user profile" model when you want to
store additional information about each user. Unfortunately, this doesn't work
at all if you need multiple user models with different information in each.
It's also a bit of a pain to make sure a profile exists and ``get_profile()``
can sometimes introduce extra database queries.

.. _Django-Model-Utils: http://bitbucket.org/carljm/django-model-utils/


Requirements and Installation
=============================

Django-User-Extension requires:

    - Django
    - Django-Model-Utils
    - setuptools or preferably `distribute <http://pypi.python.org/pypi/distribute/>`_

Installation is as simple as::

    pip install django-user-extension


Source
------
You can install the latest development version from the `hg repository`_ with::

    pip install -e hg+http://code.db-init.com/django-user-extension

Or from a tarball_ with::

    pip install django-user-extension==dev

.. _hg repository: http://bitbucket.org/dbinit/django-user-extension/
.. _tarball: http://bitbucket.org/dbinit/django-user-extension/get/tip.gz#egg=django-user-extension-dev


Usage
=====

Django-User-Extension provides a modified authentication ModelBackend class
that resolves the correct User subclass. This will ensure that ``request.user``
represents your subclass model. Simply add this to your ``settings.py``::

    AUTHENTICATION_BACKENDS = ('user_extension.backends.SubUserModelBackend',)

Also provided is a modified admin UserAdmin class that will allow you to easily
add your subclasses to the Django admin. If you try to use the default
UserAdmin you'll get an error message when add any of your custom fields to
``fieldsets``. Make sure you also add any required fields to ``add_fieldsets``.
You can use it like this in your ``admin.py``::

    from user_extension.admin import SubUserAdmin

    class CustomUserAdmin(SubUserAdmin):
        fieldsets = SubUserAdmin.fieldsets[:2] + (
            (None, {
                'fields': ('picture',)
            }),
        ) + SubUserAdmin.fieldsets[2:]
        add_fieldsets = SubUserAdmin.add_fieldsets + (
            (None, {
                'fields': ('picture',)
            }),
        )
