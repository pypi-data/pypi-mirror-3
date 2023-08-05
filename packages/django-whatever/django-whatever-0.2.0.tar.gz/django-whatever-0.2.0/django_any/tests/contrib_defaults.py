# -*- coding: utf-8; -*-
from django.db import models
from django.test import TestCase
import datetime
from decimal import Decimal
from django_any.contrib.default import any_model_with_defaults
from django.db.models.fields import NOT_PROVIDED
from django.core.files.base import ContentFile
from django_any.tests.model_creation_simple import SimpleModel


class SimpleModelWithDefaults(models.Model):
    big_integer_field = models.BigIntegerField(default=8223372036854775807)
    char_field = models.CharField(max_length=5, default='USSR')
    boolean_field = models.BooleanField(default=True)
    comma_separated_field = models.CommaSeparatedIntegerField(max_length=50, default='1,2,3')
    date_field = models.DateField(default=datetime.date(2010, 12, 10))
    datetime_field = models.DateTimeField(datetime.datetime.now)
    decimal_field = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.5'))
    email_field = models.EmailField(default='admin@dev.null')
    float_field = models.FloatField(default=0.7)
    integer_field = models.IntegerField(default=42)
    ip_field = models.IPAddressField(default='127.0.0.1')
    null_boolead_field = models.NullBooleanField(default=None)
    positive_integer_field = models.PositiveIntegerField(default=4)
    small_integer = models.PositiveSmallIntegerField(default=1)
    slug_field = models.SlugField(default='any_model_default')
    text_field = models.TextField(default='Lorem ipsum')
    time_field = models.TimeField(default=datetime.time(hour=11, minute=14))
    url_field = models.URLField(verify_exists=False, default='http://yandex.ru')

    class Meta:
        app_label = 'django_any'


class AnyModelWithDefaults(TestCase):
    sample_args = dict(
        big_integer_field = 1,
        char_field = 'USA',
        boolean_field = False,
        comma_separated_field = '5,6,7',
        date_field = datetime.date(2012, 12, 10),
        datetime_field = datetime.datetime(1985, 12, 10),
        decimal_field = Decimal('1.5'),
        email_field = 'root@dev.null',
        float_field = 1.5,
        integer_field = 777,
        ip_field = '1.2.3.4',
        null_boolead_field = True,
        positive_integer_field = 777,
        small_integer = 12,
        slug_field = 'some_model',
        text_field = 'Here I come',
        time_field = datetime.time(hour=9, minute=10, second=11),
        url_field = 'http://google.com',
    )

    def test_default_provided_called_with_no_args(self):
        result = any_model_with_defaults(SimpleModelWithDefaults)

        self.assertEqual(type(result), SimpleModelWithDefaults)
        self.assertEqual(len(result._meta.fields), len(SimpleModelWithDefaults._meta.local_fields))

        for field, original_field in zip(result._meta.fields, SimpleModelWithDefaults._meta.local_fields):
            value = getattr(result, field.name)
            if field.name != 'null_boolead_field':
                self.assertTrue(value is not None, "%s is uninitialized" % field.name)
            self.assertTrue(isinstance(field, original_field.__class__), "%s has correct field type" % field.name)
            if original_field.default is not NOT_PROVIDED:
                self.assertEqual(original_field.default, value)

    def test_default_provided_called_with_args(self):
        result = any_model_with_defaults(SimpleModelWithDefaults, **self.sample_args)

        for field, original_field in zip(result._meta.fields, SimpleModelWithDefaults._meta.local_fields):
            self.assertNotEqual(original_field.default, getattr(result, field.name))

