Additional features
===================

django-any provides clean API for creating users and authenticating as users.


Creating users
--------------

.. currentmodule:: django_any.contrib

.. function:: any_user(password=None, permissions=[], groups=[], **kwargs)

    Without arguments it creates non-superuser and non-staff active user.
    Function can simultaneusly grant permissions to user and assign him to specified groups
    (groups and permissons are not created and should exist prior to function call).
    You can also provide any key-valued arguments, which ``User`` model takes.

    .. code-block:: django

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

.. currentmodule:: django_any.test

Django-whatever has custom test clent, that extends default django client.
It provides two useful methods for authorization and forms posting.

.. function:: login_as(self, **kwargs):

    Log into site as random user. Key-valued arguments are the same as for ``any_user`` function.
    To log in as specific user, provide argument ``user`` (note, that user password will be reset).

    .. code-block:: django

        from django_any.test import Client
        self.client = Client()
        # log in as admin
        self.client.login_as(is_superuser=True)

        # log in as specific user
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.client.login_as(user=user)


.. _post_any_data:
.. function:: post_any_data(self, url, extra=None, context_forms=_request_context_forms, **kwargs):

    Posts random froms data to ``url``. Additional data can be passed in dictionary format to ``extra`` argument.
    By default, it's assumed that forms are rendered by same url, their names and default values are taken
    from context and can be overriden by ``context_forms`` argument.


Creating models with default values
-----------------------------------

Basic ``any_model`` provides totally random values that pass validation and meet requiremnts of creation,
but sometimes it's useful to keep defaults. In those cases it's recommended to use ``any_model_with_defaults``.

.. function:: any_model_with_defaults(modelClass, **kwargs):

    .. code-block:: django

        from django_any.contrib import any_model_with_defaults

        #models.py
        class Poll(models.Model):
            question = models.CharField(max_length=200)
            pub_date = models.DateTimeField('date published', defalut=datetime.datetime(2000, 12, 10))

        #tests.py
        poll = any_model_with_defaults(Poll)

    Note, that ``question`` value is random, but ``pub_date`` is taken from ``default`` attribute::

        'question': 'HJ:34KW<DGdfSgfL67KVRD:'
        'pub_date': datetime.datetime(2000, 12, 10)
