# -*- coding: utf-8 -*-
import sys

from django.core.files import File
from django.db.models import ForeignKey, OneToOneField, Model, FileField
from django.db.models.fields import *

# need to be after django.db.models.fields import *
from django_dynamic_fixture.django_helper import get_related_model, \
    field_has_choices, field_has_default_value, get_fields_from_model, \
    print_field_values, get_many_to_many_fields_from_model, \
    get_unique_model_name, get_unique_field_name, is_model_abstract, \
    field_is_a_parent_link


class UnsupportedFieldError(Exception):
    "DynamicFixture does not support this field."

class InvalidConfigurationError(Exception):
    "The specified configuration for the field can not be applied or it is bugged."

class InvalidManyToManyConfigurationError(Exception):
    "M2M attribute configuration must be a number or a list of DynamicFixture or model instances."

class BadDataError(Exception):
    "The data passed to a field has some problem (not unique or invalid) or a required attribute is in ignore list."

class InvalidModelError(Exception):
    "Invalid Model: The class is not a model or it is abstract."


class DataFixture(object):
    """
    Responsibility: return a valid data for a Django Field, according to its type, model class, constraints etc.
    
    You must create a separated method to generate data for an specific field. For a field called 'MyField', 
    the method must be: 
    def myfield_config(self, field, key): return 'some value'
    @field: Field object.
    @key: string that represents a unique name for a Field, considering app, model and field names.
    """

    def _field_fixture_template(self, field_class):
        return '%s_config' % (field_class.__name__.lower(),)

    def _field_fixture_factory(self, field_class):
        try:
            fixture = self._field_fixture_template(field_class)
            getattr(self, fixture)
            return fixture
        except AttributeError:
            if len(field_class.__bases__) > 0:
                parent_class = field_class.__bases__[0] # field must not have multiple inheritance
                return self._field_fixture_factory(parent_class)
            else:
                return None

    def new(self, field):
        "Get a unique and valid data for the field."
        config = self._field_fixture_factory(field.__class__)
        is_supported_field = config != None
        if is_supported_field:
            key = get_unique_field_name(field)
            data = eval('self.%s(field, "%s")' % (config, key,))
        else:
            if field.null:
                data = None # a workaround for versatility
            else:
                raise UnsupportedFieldError(get_unique_field_name(field)), None, sys.exc_info()[2]
        return data


class DynamicFixture(object):
    """
    Responsibility: create a valid model instance according to the given configuration.
    """

    def __init__(self, data_fixture=None, fill_nullable_fields=True, validate_models=False, validate_args=False,
                 ignore_fields=[], number_of_laps=1,
                 print_errors=True, model_path=[], **kwargs):
        """
        @data_fixture: algorithm to fill field data.
        @fill_nullable_fields: flag to decide if nullable fields must be filled with data.
        @validate_models: flag to decide if the model_instance.full_clean() must be called before saving the object.
        @ignore_fields: list of field names that must not be filled with data.
        @number_of_laps: number of laps for each cyclic dependency.
        @print_errors: flag to determine if the model data must be printed to console on errors. For some scripts is interesting to disable it.
        @model_path: internal variable used to control the cycles of dependencies.
        """
        self.data_fixture = data_fixture
        self.fill_nullable_fields = fill_nullable_fields
        self.validate_models = validate_models
        self.validate_args = validate_args
        self.ignore_fields = ignore_fields
        self.number_of_laps = number_of_laps
        self.print_errors = print_errors
        self.model_path = model_path
        self.kwargs = kwargs

    def _process_field_with_customized_fixture(self, field, fixture, persist_dependencies):
        "Set a custom value to a field."
        if isinstance(fixture, DynamicFixture): # DynamicFixture (F)
            if not fixture.data_fixture:
                fixture.data_fixture = self.data_fixture # FIXME: temp bugfix
            next_model = get_related_model(field)
            if persist_dependencies:
                data = fixture.get(next_model)
            else:
                data = fixture.new(next_model, persist_dependencies=persist_dependencies)
        elif isinstance(fixture, DataFixture): # DataFixture
            next_model = get_related_model(field)
            data = fixture.new(next_model)
        elif callable(fixture): # callable with the field as parameters
            data = fixture(field)
        else: # attribute value
            if hasattr(field, 'auto_now_add') and field.auto_now_add:
                field.auto_now_add = False
            if hasattr(field, 'auto_now') and field.auto_now:
                field.auto_now = False
            data = fixture
        return data

    def _process_field_with_default_fixture(self, field, model_class, persist_dependencies):
        "The field has no custom value, so the default behavior of the tool is applied."
        if field.null and not self.fill_nullable_fields:
            return None

        if field_has_default_value(field):
            if callable(field.default):
                data = field.default() # datetime default can receive a function: datetime.now
            else:
                data = field.default

        elif field_has_choices(field):
            data = field.choices[0][0] # key of the first choice

        elif isinstance(field, (ForeignKey, OneToOneField)):
            if field_is_a_parent_link(field):
                return None
            next_model = get_related_model(field)
            occurrences = self.model_path.count(next_model)
            if occurrences >= self.number_of_laps:
                data = None
            else:
                next_model_path = self.model_path[:]
                next_model_path.append(model_class)
                if model_class == next_model: # self reference
                    # propagate ignored_fields only for self references
                    ignore_fields = self.ignore_fields
                else:
                    ignore_fields = []
                # need a new DynamicFixture to control the cycles and ignored fields.
                fixture = DynamicFixture(data_fixture=self.data_fixture,
                                         fill_nullable_fields=self.fill_nullable_fields,
                                         validate_models=self.validate_models,
                                         validate_args=self.validate_args,
                                         ignore_fields=ignore_fields,
                                         number_of_laps=self.number_of_laps,
                                         print_errors=self.print_errors,
                                         model_path=next_model_path)
                if persist_dependencies:
                    data = fixture.get(next_model)
                else:
                    data = fixture.new(next_model, persist_dependencies=persist_dependencies)

        else:
            data = self.data_fixture.new(field)

        return data

    def _process_many_to_many_field(self, field, manytomany_field, fixture):
        "Set ManyToManyField fields with or without 'trough' option."
        next_model = get_related_model(field)
        if isinstance(fixture, int):
            amount = fixture
            for _ in range(amount):
                next_instance = self.get(next_model)
                try:
                    manytomany_field.add(next_instance)
                except AttributeError: # M2M with trough: ManyRelatedManager
                    next_instance.save()
        elif isinstance(fixture, list) or isinstance(fixture, tuple):
            items = fixture
            for item in items:
                if isinstance(item, DynamicFixture):
                    if not item.data_fixture:
                        item.data_fixture = self.data_fixture # FIXME: temp bugfix
                    next_instance = item.get(next_model)
                else:
                    next_instance = item
                try:
                    manytomany_field.add(next_instance)
                except AttributeError: # M2M with trough: ManyRelatedManager
                    next_instance.save()
        else:
            raise InvalidManyToManyConfigurationError('Field: %s' % field.name, fixture), None, sys.exc_info()[2]

    def _validate_kwargs(self, model_class, kwargs):
        for field_name in kwargs.keys():
            try:
                model_class._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                raise InvalidConfigurationError('Field "%s" does not exist.' % field_name), None, sys.exc_info()[2]

    def new(self, model_class, persist_dependencies=True, **kwargs):
        "Create an instance filled with data without persist it."
        if self.validate_args:
            self._validate_kwargs(model_class, kwargs)
        kwargs.update(self.kwargs)
        instance = model_class()
        if not isinstance(instance, Model):
            raise InvalidModelError(get_unique_model_name(model_class)), None, sys.exc_info()[2]
        for field in get_fields_from_model(model_class):
            if isinstance(field, AutoField) and 'id' not in kwargs: continue
            if field.name in self.ignore_fields: continue
            if field.name in kwargs:
                config = kwargs[field.name]
                try:
                    data = self._process_field_with_customized_fixture(field, config, persist_dependencies)
                except Exception as e:
                    raise InvalidConfigurationError(get_unique_field_name(field), e), None, sys.exc_info()[2]
            else:
                data = self._process_field_with_default_fixture(field, model_class, persist_dependencies)

            if isinstance(field, FileField):
                django_file = data
                if isinstance(django_file, File):
                    setattr(instance, field.name, data.name) # set the attribute
                    if django_file.file.mode != 'rb':
                        django_file.file.close() # this file may be open in another mode, for example, in a+b
                        file = open(django_file.file.name, 'rb') # to save the file it must be open in rb mode
                        django_file.file = file # we update the reference to the rb mode opened file
                    getattr(instance, field.name).save(django_file.name, django_file) # save the file into the file storage system
                    django_file.close()
                else: # string (saving just a name in the file, without saving the file to the storage file system
                    setattr(instance, field.name, data)
            else:
                setattr(instance, field.name, data)
        return instance

    def get(self, model_class, **kwargs):
        "Create an instance with data and persist it."
        if self.validate_args:
            self._validate_kwargs(model_class, kwargs)
        kwargs.update(self.kwargs)
        instance = self.new(model_class, **kwargs)
        if is_model_abstract(model_class):
            raise InvalidModelError(get_unique_model_name(model_class)), None, sys.exc_info()[2]
        try:
            if self.validate_models:
                instance.full_clean()
            instance.save()
        except Exception as e:
            if self.print_errors:
                print_field_values(instance)
            raise BadDataError(get_unique_model_name(model_class), e), None, sys.exc_info()[2]
        for field in get_many_to_many_fields_from_model(model_class):
            if field.name in kwargs.keys():
                manytomany_field = getattr(instance, field.name)
                fixture = kwargs[field.name]
                try:
                    self._process_many_to_many_field(field, manytomany_field, fixture)
                except InvalidManyToManyConfigurationError as e:
                    raise e, None, sys.exc_info()[2]
                except Exception as e:
                    raise InvalidManyToManyConfigurationError(get_unique_field_name(field), e), None, sys.exc_info()[2]
        return instance

