# -*- coding: utf-8; mode: django -*-
"""
Test model creation with FileField
"""
import os
from django.db import models
from django.test import TestCase
from django_any import any_model

class ModelWithFileFieldUploadToString(models.Model):
    file_field = models.FileField(upload_to='sample_subdir')

    class Meta:
        app_label = 'django_any'


def callable_upload_to(instance, filename):
    return os.path.join('sample_subdir', filename)


class ModelWithFileFieldUploadToCallable(models.Model):
    file_field = models.FileField(upload_to=callable_upload_to)

    class Meta:
        app_label = 'django_any'


class FileFiledUploadTo(TestCase):

    def test_created_model_with_filefield_string_upload_to(self):
        model = any_model(ModelWithFileFieldUploadToString)
        self.assertEqual(model.file_field, 'sample_file.txt')

    def test_created_model_with_filefield_callable_upload_to(self):
        model = any_model(ModelWithFileFieldUploadToCallable)
        self.assertEqual(model.file_field, 'sample_file.txt')

