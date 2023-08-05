Installation
============

.. warning::  To retain backwards compatibility with code written for ``django-any``, ``django-whatever`` package
              shares the same namespace, so make sure to remove previous ``django_any`` installations if you have any.


* Install the package with your python package manager::

    pip install django-whatever

* Add ``'django_any'`` to your ``INSTALLED_APPS`` setting (it's not a typo, we use same app name as ``django_any``)::

    INSTALLED_APPS = (
        ...
        "django_any",
        ...
    )

