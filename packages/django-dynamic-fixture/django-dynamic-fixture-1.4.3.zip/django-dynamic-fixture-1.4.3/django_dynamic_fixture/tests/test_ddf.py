# -*- coding: utf-8 -*-

from django.test import TestCase

from django.db import models
from django.db import IntegrityError

from datetime import datetime, time, date
from decimal import Decimal

from django_dynamic_fixture.models import *
from django_dynamic_fixture.ddf import *


class DDFTestCase(TestCase):
    def setUp(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture())


class NewCreateAModelInstanceTest(DDFTestCase):

    def test_new_create_a_non_saved_instance_of_the_model(self):
        instance = self.ddf.new(EmptyModel)
        self.assertTrue(isinstance(instance, EmptyModel))
        self.assertEquals(None, instance.id)


class NewFullFillAttributesWithAutoDataTest(DDFTestCase):

    def test_new_fill_number_fields_with_numbers(self):
        instance = self.ddf.new(ModelWithNumbers)
        self.assertTrue(isinstance(instance.integer, int))
        self.assertTrue(isinstance(instance.smallinteger, int))
        self.assertTrue(isinstance(instance.positiveinteger, int))
        self.assertTrue(isinstance(instance.positivesmallinteger, int))
        self.assertTrue(isinstance(instance.biginteger, int))
        self.assertTrue(isinstance(instance.float, float))

    def test_decimal_deal_with_max_digits(self):
        # max_digits=2, decimal_places=1
        # value 10 must be a problem, need to restart the counter: 10.0 has 3 digits
        for i in range(12):
            instance = self.ddf.new(ModelWithNumbers)
            self.assertTrue(isinstance(instance.decimal, Decimal))

    def test_new_fill_string_fields_with_unicode_strings(self):
        instance = self.ddf.new(ModelWithStrings)
        self.assertTrue(isinstance(instance.string, unicode))
        self.assertTrue(isinstance(instance.text, unicode))
        self.assertTrue(isinstance(instance.slug, unicode))
        self.assertTrue(isinstance(instance.commaseparated, unicode))

    def test_new_truncate_strings_to_max_length(self):
        for i in range(12): # truncate start after the 10 object
            instance = self.ddf.new(ModelWithStrings)
            self.assertTrue(isinstance(instance.string, unicode))
            self.assertTrue(len(instance.string) == 1)

    def test_new_fill_boolean_fields_with_False_and_None(self):
        instance = self.ddf.new(ModelWithBooleans)
        self.assertEquals(False, instance.boolean)
        self.assertEquals(None, instance.nullboolean)

    def test_new_fill_time_related_fields_with_current_values(self):
        instance = self.ddf.new(ModelWithDateTimes)
        self.assertTrue(date.today() >= instance.date)
        self.assertTrue(datetime.now() >= instance.time)
        self.assertTrue(datetime.now() >= instance.datetime)

    def test_new_fill_formatted_strings_fields_with_basic_values(self):
        instance = self.ddf.new(ModelWithFieldsWithCustomValidation)
        self.assertTrue(isinstance(instance.email, str))
        self.assertTrue(isinstance(instance.url, str))
        self.assertTrue(isinstance(instance.ip, str))
        self.assertTrue(isinstance(instance.xml, str))

    def test_new_fill_file_fields_with_basic_strings(self):
        instance = self.ddf.new(ModelWithFileFields)
        self.assertTrue(isinstance(instance.filepath, str))
        self.assertTrue(isinstance(instance.file.path, unicode))
        try:
            import pil
            # just test it if the PIL package is installed
            self.assertTrue(isinstance(instance.image, str))
        except ImportError:
            pass


class NewFullFilledModelInstanceWithSequencialAutoDataTest(DDFTestCase):
    def test_new_fill_integer_fields_sequencially_by_attribute(self):
        instance = self.ddf.new(ModelWithNumbers)
        self.assertEquals(1, instance.integer)
        self.assertEquals(1, instance.positiveinteger)

        instance = self.ddf.new(ModelWithNumbers)
        self.assertEquals(2, instance.integer)
        self.assertEquals(2, instance.positiveinteger)

        instance = self.ddf.new(ModelWithNumbers)
        self.assertEquals(3, instance.integer)
        self.assertEquals(3, instance.positiveinteger)

    def test_new_fill_string_with_sequences_of_numbers_by_attribute(self):
        instance = self.ddf.new(ModelWithStrings)
        self.assertEquals('1', instance.string)
        self.assertEquals('1', instance.text)
        instance = self.ddf.new(ModelWithStrings)
        self.assertEquals('2', instance.string)
        self.assertEquals('2', instance.text)


class GetDealWithPrimaryKeyTest(DDFTestCase):

    def test_get_use_database_id_by_default(self):
        instance = self.ddf.get(ModelForNullableTest)
        self.assertNotEquals(None, instance.id)
        self.assertNotEquals(None, instance.pk)

    def test_get_use_given_id(self):
        instance = self.ddf.new(ModelForNullableTest, id=99998)
        self.assertEquals(99998, instance.id)
        self.assertEquals(99998, instance.pk)


class NewFullFillAttributesWithDefaultDataTest(DDFTestCase):

    def test_fill_field_with_default_data(self):
        instance = self.ddf.new(ModelWithDefaultValues)
        self.assertEquals(3, instance.integer_with_default)

    def test_fill_field_with_possible_choices(self):
        instance = self.ddf.new(ModelWithDefaultValues)
        self.assertEquals('a', instance.string_with_choices)

    def test_fill_field_with_default_value_even_if_field_is_foreign_key(self):
        instance = self.ddf.new(ModelWithDefaultValues)
        self.assertEquals(None, instance.foreign_key_with_default)

    def test_fill_field_with_default_data_and_choices_must_consider_default_data_instead_choices(self):
        instance = self.ddf.new(ModelWithDefaultValues)
        self.assertEquals('b', instance.string_with_choices_and_default)


class NewFullFillAttributesWithCustomDataTest(DDFTestCase):

    def test_fields_are_filled_with_custom_attributes(self):
        self.assertEquals(9, self.ddf.new(ModelWithNumbers, integer=9).integer)
        self.assertEquals('7', self.ddf.new(ModelWithStrings, string='7').string)
        self.assertEquals(True, self.ddf.new(ModelWithBooleans, boolean=True).boolean)

    def test_fields_can_be_filled_by_functions(self):
        instance = self.ddf.new(ModelWithStrings, string=lambda field: field.name)
        self.assertEquals('string', instance.string)

    def test_invalid_configuration_raise_an_error(self):
        self.assertRaises(InvalidConfigurationError, self.ddf.new, ModelWithNumbers, integer=lambda x: ''.invalidmethod())

    def test_bad_data_raise_an_error(self):
        self.ddf.get(ModelWithNumbers, integer=50000)
        self.assertRaises(BadDataError, self.ddf.get, ModelWithNumbers, integer=50000)


class NewAlsoCreatesRelatedObjectsTest(DDFTestCase):

    def test_new_fill_foreignkey_fields(self):
        instance = self.ddf.new(ModelWithRelationships)
        self.assertTrue(isinstance(instance.foreignkey, ModelRelated))

    def test_new_fill_onetoone_fields(self):
        instance = self.ddf.new(ModelWithRelationships)
        self.assertTrue(isinstance(instance.onetoone, ModelRelated))

#        TODO
#    def test_new_fill_genericrelations_fields(self):
#        instance = self.ddf.new(ModelWithRelationships)
#        self.assertTrue(isinstance(instance.foreignkey, ModelRelated))


class NewCanCreatesCustomizedRelatedObjectsTest(DDFTestCase):

    def test_customizing_nullable_fields_for_related_objects(self):
        instance = self.ddf.new(ModelWithRelationships, selfforeignkey=DynamicFixture(fill_nullable_fields=False))
        self.assertTrue(isinstance(instance.integer, int))
        self.assertEquals(None, instance.selfforeignkey.integer)


class NewDealWithSelfReferencesTest(DDFTestCase):

    def test_new_create_by_default_only_1_lap_in_cycle(self):
        instance = self.ddf.new(ModelWithRelationships)
        self.assertNotEquals(None, instance.selfforeignkey) # 1 cycle
        self.assertEquals(None, instance.selfforeignkey.selfforeignkey) # 2 cycles

    def test_new_create_n_laps_in_cycle(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), number_of_laps=2)
        instance = self.ddf.new(ModelWithRelationships)
        self.assertNotEquals(None, instance.selfforeignkey) # 1 cycle
        self.assertNotEquals(None, instance.selfforeignkey.selfforeignkey) # 2 cycles
        self.assertEquals(None, instance.selfforeignkey.selfforeignkey.selfforeignkey) # 3 cycles


class NewDealWithCyclicDependenciesTest(DDFTestCase):

    def test_new_create_by_default_only_1_lap_in_cycle(self):
        c = self.ddf.new(ModelWithCyclicDependency)
        self.assertNotEquals(None, c.d) # 1 cycle
        self.assertEquals(None, c.d.c) # 2 cycles

    def test_new_create_n_laps_in_cycle(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), number_of_laps=2)
        c = self.ddf.new(ModelWithCyclicDependency)
        self.assertNotEquals(None, c.d)
        self.assertNotEquals(None, c.d.c) # 1 cycle
        self.assertNotEquals(None, c.d.c.d) # 2 cycles
        self.assertEquals(None, c.d.c.d.c) # 3 cycles


class NewDealWithInheritanceTest(DDFTestCase):

    def test_new_must_not_raise_an_error_if_model_is_abstract(self):
        self.ddf.new(ModelAbstract) # it does not raise an exceptions

    def test_get_must_raise_an_error_if_model_is_abstract(self):
        self.assertRaises(InvalidModelError, self.ddf.get, ModelAbstract)

    def test_get_must_fill_parent_fields_too(self):
        instance = self.ddf.get(ModelParent)
        self.assertTrue(isinstance(instance.integer, int))
        self.assertEquals(1, ModelParent.objects.count())

    def test_get_must_fill_grandparent_fields_too(self):
        instance = self.ddf.get(ModelChild)
        self.assertTrue(isinstance(instance.integer, int))
        self.assertEquals(1, ModelParent.objects.count())
        self.assertEquals(1, ModelChild.objects.count())

    def test_get_must_ignore_parent_link_attributes_but_the_parent_object_must_be_created(self):
        instance = self.ddf.get(ModelChildWithCustomParentLink)
        self.assertTrue(isinstance(instance.integer, int))
        self.assertEquals(1, instance.my_custom_ref.id)
        self.assertEquals(1, ModelParent.objects.count())
        self.assertEquals(1, ModelChildWithCustomParentLink.objects.count())

    # TODO: need to check these tests. Here we are trying to simulate a bug with parent_link attribute
    def test_get_0(self):
        instance = self.ddf.get(ModelWithRefToParent)
        self.assertEquals(1, ModelWithRefToParent.objects.count())
        self.assertEquals(1, ModelParent.objects.count())
        self.assertTrue(isinstance(instance.parent, ModelParent))

    def test_get_1(self):
        instance = self.ddf.get(ModelWithRefToParent, parent=self.ddf.get(ModelChild))
        self.assertEquals(1, ModelWithRefToParent.objects.count())
        self.assertEquals(1, ModelParent.objects.count())
        self.assertEquals(1, ModelChild.objects.count())
        self.assertTrue(isinstance(instance.parent, ModelChild))

    def test_get_2(self):
        instance = self.ddf.get(ModelWithRefToParent, parent=self.ddf.get(ModelChildWithCustomParentLink))
        self.assertEquals(1, ModelWithRefToParent.objects.count())
        self.assertEquals(1, ModelParent.objects.count())
        self.assertEquals(1, ModelChildWithCustomParentLink.objects.count())
        self.assertTrue(isinstance(instance.parent, ModelChildWithCustomParentLink))


class NewIgnoringNullableFieldsTest(DDFTestCase):

    def test_new_do_not_fill_nullable_fields_if_we_do_not_want_to(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), fill_nullable_fields=False)
        instance = self.ddf.new(ModelForNullableTest)
        self.assertNotEquals(None, instance.not_nullable)
        self.assertEquals(None, instance.nullable)


class NewIgnoreFieldsInIgnoreListTest(DDFTestCase):

    def test_new_do_not_fill_ignored_fields(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), ignore_fields=['not_required', 'not_required_with_default'])
        instance = self.ddf.new(ModelForIgnoreListTest)
        self.assertEquals(None, instance.not_required)
        self.assertNotEquals(None, instance.not_required_with_default)
        # not ignored fields
        self.assertNotEquals(None, instance.required)
        self.assertNotEquals(None, instance.required_with_default)

    def test_get_raise_an_error_if_a_required_field_is_in_ignore_list(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), ignore_fields=['required', 'required_with_default'])
        self.assertRaises(BadDataError, self.ddf.get, ModelForIgnoreListTest)

    def test_ignore_fields_are_propagated_to_self_references(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), ignore_fields=['not_required', 'nullable'])
        instance = self.ddf.new(ModelForIgnoreListTest)
        self.assertEquals(None, instance.not_required)
        self.assertEquals(None, instance.self_reference.not_required)

    def test_ignore_fields_are_not_propagated_to_different_references(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), ignore_fields=['not_required', 'nullable'])
        instance = self.ddf.new(ModelForIgnoreListTest)
        self.assertNotEquals(None, instance.different_reference.nullable)


class GetFullFilledModelInstanceAndPersistTest(DDFTestCase):

    def test_get_create_and_save_a_full_filled_instance_of_the_model(self):
        instance = self.ddf.get(ModelWithRelationships)
        self.assertTrue(isinstance(instance, ModelWithRelationships))
        self.assertNotEquals(None, instance.id)
        # checking unique problems
        another_instance = self.ddf.get(ModelWithRelationships)
        self.assertTrue(isinstance(another_instance, ModelWithRelationships))
        self.assertNotEquals(None, another_instance.id)

    def test_get_create_and_save_related_fields(self):
        instance = self.ddf.get(ModelWithRelationships)
        self.assertNotEquals(None, instance.selfforeignkey)
        self.assertNotEquals(None, instance.foreignkey)
        self.assertNotEquals(None, instance.onetoone)


class ManyToManyRelationshipTest(DDFTestCase):
    def test_new_ignore_many_to_many_configuratios(self):
        instance = self.ddf.new(ModelWithRelationships, manytomany=3)
        instance.save()
        self.assertEquals(0, instance.manytomany.all().count())

    def test_get_ignore_many_to_many_configuratios(self):
        instance = self.ddf.get(ModelWithRelationships, manytomany=3)
        self.assertEquals(3, instance.manytomany.all().count())

    def test_many_to_many_configuratios_accept_list_of_dynamic_filters(self):
        instance = self.ddf.get(ModelWithRelationships, manytomany=[DynamicFixture(integer=1000), DynamicFixture(integer=1001)])
        self.assertEquals(2, instance.manytomany.all().count())
        self.assertEquals(1000, instance.manytomany.all()[0].integer)
        self.assertEquals(1001, instance.manytomany.all()[1].integer)

    def test_many_to_many_configuratios_accept_list_of_instances(self):
        b1 = self.ddf.get(ModelRelated, integer=1000)
        b2 = self.ddf.get(ModelRelated, integer=1001)
        instance = self.ddf.get(ModelWithRelationships, manytomany=[b1, b2])
        self.assertEquals(2, instance.manytomany.all().count())
        self.assertEquals(1000, instance.manytomany.all()[0].integer)
        self.assertEquals(1001, instance.manytomany.all()[1].integer)

    def test_invalid_many_to_many_configuration(self):
        self.assertRaises(InvalidManyToManyConfigurationError, self.ddf.get, ModelWithRelationships, manytomany='a')


class CustomFieldsTest(DDFTestCase):
    def test_new_field_that_extends_django_field_must_be_supported(self):
        instance = self.ddf.new(ModelWithCustomFields)
        self.assertEquals(1, instance.x)

    def test_unsupported_field_is_filled_with_null_if_it_is_possible(self):
        instance = self.ddf.new(ModelWithCustomFields)
        self.assertEquals(None, instance.y)

    def test_unsupported_field_raise_an_error_if_it_does_not_accept_null_value(self):
        self.assertRaises(UnsupportedFieldError, self.ddf.new, ModelWithUnsupportedField)


class MyClass(object): pass

class ExceptionsLayoutMessagesTest(DDFTestCase):
    def test_UnsupportedFieldError(self):
        try:
            self.ddf.new(ModelWithUnsupportedField)
            self.fail()
        except UnsupportedFieldError as e:
            self.assertEquals("""django_dynamic_fixture.ModelWithUnsupportedField.z""",
                              str(e))

    def test_BadDataError(self):
        self.ddf = DynamicFixture(data_fixture=DefaultDataFixture(), ignore_fields=['required', 'required_with_default'])
        try:
            self.ddf.get(ModelForIgnoreListTest)
            self.fail()
        except BadDataError as e:
            self.assertEquals("""('django_dynamic_fixture.ModelForIgnoreListTest', IntegrityError('django_dynamic_fixture_modelforignorelisttest.required may not be NULL',))""",
                              str(e))

    def test_InvalidConfigurationError(self):
        try:
            self.ddf.new(ModelWithNumbers, integer=lambda x: ''.invalidmethod())
            self.fail()
        except InvalidConfigurationError as e:
            self.assertEquals("""('django_dynamic_fixture.ModelWithNumbers.integer', AttributeError("'str' object has no attribute 'invalidmethod'",))""",
                              str(e))

    def test_InvalidManyToManyConfigurationError(self):
        try:
            self.ddf.get(ModelWithRelationships, manytomany='a')
            self.fail()
        except InvalidManyToManyConfigurationError as e:
            self.assertEquals("""('Field: manytomany', 'a')""",
                              str(e))

    def test_InvalidModelError(self):
        try:
            self.ddf.get(ModelAbstract)
            self.fail()
        except InvalidModelError as e:
            self.assertEquals("""django_dynamic_fixture.ModelAbstract""",
                              str(e))

    def test_InvalidModelError_for_common_object(self):
        try:
            self.ddf.new(MyClass)
            self.fail()
        except InvalidModelError as e:
            self.assertEquals("""django_dynamic_fixture.tests.test_ddf.MyClass""",
                              str(e))


class SanityTest(DDFTestCase):
    def test_create_lots_of_models_to_verify_data_unicity_errors(self):
        for i in range(1000):
            self.ddf.get(ModelWithNumbers)
