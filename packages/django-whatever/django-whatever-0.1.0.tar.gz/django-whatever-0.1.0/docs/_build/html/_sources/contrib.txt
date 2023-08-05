Additional features
===================

django-any provides clean API for creating users and authenticating as users.


Creating users
--------------

.. _any_user

``any_user(password=None, permissions=[], groups=[], **kwargs)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Without arguments it creates non-superuser and non-staff active user.
Function can simultaneusly grant permissions to user and assign him to specified groups
(groups and permissons are not created and should exist prior to function call).
You can also provide any key-valued arguments, which ``User`` model takes.

Examples
~~~~~~~~
::

    from django_any.contrib import any_user
    # create random user
    foo = any_user()

    # create inactive superuser
    any_user(is_superuser=True, is_active=False, is_staff=True)

    # create user with permissions 'can_add' and 'can_delete' in app books
    any_user(permissions=['books.can_add', 'books.can_delete'])

    # create user in group 'Special users'
    any_user(groups=['Special users'])


Custom test client
------------------

Django any has custom test clent, that extends default django client.
It provides two useful methods for authorisation and posting forms.

.. _login_as

``login_as(self, **kwargs):``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Log into site as random user. Key-valued arguments are the same as for ``any_user`` function.

Example
~~~~~~~~
::

        from any_model.test import Client
        self.client = Client()
        # log in as admin
        self.client.login_as(is_superuser=True)


.. _post_any_data:
``post_any_data(self, url, extra=None, context_forms=_request_context_forms, **kwargs):``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Posts random froms data to ``url``. Additional data can be passed in dictionary format to ``extra`` argument.
By default, it's assumed that forms are rendered by same url, their names and default values are taken
from context and can be overriden by ``context_forms`` argument.

