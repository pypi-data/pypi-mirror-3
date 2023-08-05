django-whatever (fork of django-any)
====================================

**NB:** django-whatever is a friendly fork of ``django-any`` package by Mikhail Podgurskiy (kmmbvnr)

django-any is explicit replacement for old-style, big and error-prone
implicit fixture files.

django-any allows you to specify only fields important for tests
and fills the rest randomly with acceptable values.

It makes tests clean and easy to understand, without reading fixture files.
::

    from django_any import any_model

    class TestMyShop(TestCase):
        def test_order_updates_user_account(self):
            account = any_model(Account, amount=25, user__is_active=True)
            order = any_model(Order, user=account.user, amount=10)
            order.proceed()

            account = Account.objects.get(pk=account.pk)
            self.assertEquals(15, account.amount)

Contents
--------

.. toctree::
   :maxdepth: 1

   installation
   usage
   forms
   contrib
   debugging
   changelog

Authors
-------

* kmmbvnr https://github.com/kmmbvnr
* Vitaa https://github.com/Vitaa

Contributors
^^^^^^^^^^^^

* Coagulant (fork maintainer) https://github.com/coagulant

