from django import test
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from generic_helpers.models import GenericRelationModel, models
from generic_helpers.tests.models import *


class ModelTest(test.TestCase):
    def setUp(self):
        load_test_data()

    def test_is_instance(self):
        assert issubclass(Bar, GenericRelationModel)

    def test_content_object_attr_exists(self):
        self.assertTrue(hasattr(Bar, 'content_object'))
        self.assertTrue(type(Bar.content_object) is generic.GenericForeignKey)

    def test_object_pk_column_exists(self):
        self.assertTrue(hasattr(Bar(), 'object_pk'))

    def test_content_type_column_exists(self):
        self.assertTrue(hasattr(Bar, 'content_type'))

    def test_custom_ct_rel_error(self):
        self.assertRaises(ValueError, lambda: BadBaz())


class ManagerTest(test.TestCase):
    def setUp(self):
        load_test_data()
        self.foo = Foo.objects.all()[0]

    def test_count(self):
        self.assertEquals(FOO_NUMBER, Foo.objects.count())
        self.assertEquals(BAR_NUMBER**2, Bar.objects.count())

    def test_get_for_object_count(self):
        self.assertEquals(BAR_NUMBER, Bar.objects.get_for_object(self.foo).count())

    def test_get_for_object_type(self):
        for bar in Bar.objects.get_for_object(self.foo):
            self.assertTrue(bar.content_object == self.foo)

    def test_get_for_model(self):
        self.assertEquals(BAR_NUMBER*FOO_NUMBER, Bar.objects.get_for_model(Foo).count())

    def test_patched_filter(self):
        self.assertEquals(BAR_NUMBER, Bar.objects.filter(content_object=self.foo).count())

    def test_patched_exclude(self):
        self.assertEquals(BAR_NUMBER* (FOO_NUMBER-1), Bar.objects.exclude(content_object=self.foo).count())

    def test_custom_related_name(self):
       ct = ContentType.objects.get_for_model(self.foo)
       rl = ct._meta._name_map['ct_set_for_baz'][0].field.rel.related_name # @TODO: ?
       self.assertIn(BAZ_CT_REL, rl)