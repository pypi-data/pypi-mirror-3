# -*- coding: utf-8; mode: django -*-
"""
Test model creation with GenericForeignKey
"""
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TestCase
from django_any import any_model


class RelatedContentModel(models.Model):
    name = models.SlugField()

    class Meta:
        app_label = 'django_any'

class ModelWithGenericRelation(models.Model):
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = 'django_any'


class ContentTypeTest(TestCase):
    def test_verbose_generic_fk_creation(self):
        content_object = any_model(RelatedContentModel)
        result = any_model(ModelWithGenericRelation,
                           content_type=ContentType.objects.get_for_model(RelatedContentModel),
                           object_id=content_object.id)
        self.assertEqual(result.content_object, content_object)
        self.assertEqual(result.content_type, ContentType.objects.get_for_model(RelatedContentModel))
        self.assertEqual(result.object_id, content_object.id)

    def test_short_generic_fk_creation(self):
        content_object = any_model(RelatedContentModel)
        related_object = any_model(ModelWithGenericRelation,
                                   content_object=content_object)
        self.assertEqual(related_object.content_object, content_object)
        self.assertEqual(related_object.content_type, ContentType.objects.get_for_model(RelatedContentModel))
        self.assertEqual(related_object.object_id, content_object.id)

