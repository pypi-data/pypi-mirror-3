Forms creation
==============

You can get data for form submissions without secifying form fields
(it acs very much like :ref:`any_model <models_creation>`).

Given you have a simple contact form::

    #forms.py
    class ContactForm(forms.Form):
        subject = forms.CharField(max_length=100)
        message = forms.CharField(max_length=10)
        sender = forms.EmailField()
        cc_myself = forms.BooleanField(required=False)

You can create a random data to test that form this way::

    from django_any.forms import any_form
    post, files = any_form(ContactForm)

It will create a tuple dictionaries with ``POST`` and ``FILES`` data::

    >> post
    {'cc_myself': 'False',
     'message': 'wEqhESoSOO',
     'sender': 'bbfGIXwKrd@KPXRDCAyJD.xyR',
     'subject': 'hVocAZRuZPRHuVyWCV'
    }
    >> files
    {}

Now we can pass the data to the form and check if it validates::

    test_form = ContactForm(post, files)
    self.assertTrue(test_form.is_vlaid())


For advances usage see :ref:`post_any_data <post_any_data>`