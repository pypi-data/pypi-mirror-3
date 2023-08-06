# -*- coding: utf-8 -*-

from django.test import TestCase

from django_dynamic_fixture import new, get
from django_dynamic_fixture.models import *
from django_dynamic_fixture.django_helper import *


class DjangoHelperTest(TestCase):

    def test_get_fields_from_model(self):
        self.assertEquals(8, len(get_fields_from_model(ModelWithNumbers)))

    def test_get_field_names_from_model(self):
        self.assertEquals(8, len(get_field_names_from_model(ModelWithNumbers)))

    def test_get_many_to_many_fields_from_model(self):
        self.assertEquals(1, len(get_many_to_many_fields_from_model(ModelWithRelationships)))

    def test_get_related_model(self):
        foreignkey = get_fields_from_model(ModelWithRelationships)[1]
        get_related_model(foreignkey)

    def test_field_has_choices(self):
        integer_with_default = get_fields_from_model(ModelWithDefaultValues)[1]
        string_with_choices = get_fields_from_model(ModelWithDefaultValues)[2]
        self.assertEquals(False, field_has_choices(integer_with_default))
        self.assertEquals(True, field_has_choices(string_with_choices))

    def test_field_has_default_value(self):
        integer_with_default = get_fields_from_model(ModelWithDefaultValues)[1]
        string_with_choices = get_fields_from_model(ModelWithDefaultValues)[2]
        self.assertEquals(False, field_has_default_value(string_with_choices))
        self.assertEquals(True, field_has_default_value(integer_with_default))


class PrintFieldValuesTest(TestCase):
    def test_model_not_saved_do_not_raise_an_exception(self):
        instance = new(ModelWithNumbers)
        print_field_values(instance)

    def test_model_saved_do_not_raise_an_exception(self):
        instance = get(ModelWithNumbers)
        print_field_values(instance)
