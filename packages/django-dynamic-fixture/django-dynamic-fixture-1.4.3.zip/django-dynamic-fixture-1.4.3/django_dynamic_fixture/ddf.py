# -*- coding: utf-8 -*-
import sys

from django.core.files import File
from django.db.models import ForeignKey, OneToOneField, ManyToManyField, Model, FileField
from django.db.models.fields import *

# need to be after django.db.models.fields import *
from decimal import Decimal
from datetime import datetime, time, date, timedelta
from functools import wraps
import threading
from django_dynamic_fixture.django_helper import get_related_model, \
    field_has_choices, field_has_default_value, get_fields_from_model, \
    print_field_values, get_many_to_many_fields_from_model, \
    get_unique_model_name, get_unique_field_name, is_model_abstract, \
    is_model_class, field_is_a_parent_link


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


class AutoDataFiller(object):

    def __init__(self):
        self.__data_controller_map = {} # key => counter
        self.__locks = {} # key => lock

    # synchronized by key
    def next(self, key, cast=lambda data: data):
        if key not in self.__data_controller_map:
            self.__data_controller_map[key] = 0
            self.__locks[key] = threading.RLock()
        self.__locks[key].acquire()
        self.__data_controller_map[key] += 1
        value = cast(self.__data_controller_map[key])
        self.__locks[key].release()
        return value


class DataFixture(object):

    def new(self, field):
        "Get a unique and valid data for the field."
        raise NotImplementedError()


class DefaultDataFixture(DataFixture):

    def __init__(self):
        self.filler = AutoDataFiller()

    # numbers
    def integerfield_config(self, field, key): return self.filler.next(key)
    def smallintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def positiveintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def positivesmallintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def bigintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def floatfield_config(self, field, key): return self.filler.next(key, lambda data: float(data))
    def decimalfield_config(self, field, key):
        data = self.filler.next(key)
        number_of_digits = field.max_digits - field.decimal_places
        max_value = 10 ** number_of_digits
        data = data % max_value
        return Decimal(str(data))

    #string
    def charfield_config(self, field, key):
        data = self.filler.next(key, cast=lambda data: unicode(data))
        data = data[:field.max_length]
        return data
    def textfield_config(self, field, key): return self.charfield_config(field, key)
    def slugfield_config(self, field, key): return self.charfield_config(field, key)
    def commaseparatedintegerfield_config(self, field, key): return self.charfield_config(field, key)

    # boolean
    def booleanfield_config(self, field, key): return False
    def nullbooleanfield_config(self, field, key): return None

    # time related
    def datefield_config(self, field, key):
        return self.filler.next(key, cast=lambda data: (date.today() - timedelta(days=data)))
    def timefield_config(self, field, key):
        return self.filler.next(key, cast=lambda data: (datetime.now() - timedelta(seconds=data)))
    def datetimefield_config(self, field, key):
        return self.filler.next(key, cast=lambda data: (datetime.now() - timedelta(seconds=data)))

    # formatted strings
    def emailfield_config(self, field, key): return 'a%s@dynamicfixture.com' % (self.filler.next(key, cast=lambda data: str(data)),)
    def urlfield_config(self, field, key): return 'http://dynamicfixture%s.com' % (self.filler.next(key, cast=lambda data: str(data)),)
    def ipaddressfield_config(self, field, key):
        # TODO: better workaround (this suppose ip field is not unique)
        data = self.filler.next(key)
        a = '1'
        b = '1'
        c = '1'
        d = data % 256
        return '%s.%s.%s.%s' % (a, b, c, str(d))
    def xmlfield_config(self, field, key): return '<a>%s</a>' % (self.filler.next(key, cast=lambda data: str(data)),)

    # files
    def filepathfield_config(self, field, key): return self.filler.next(key, cast=lambda data: str(data))
    def filefield_config(self, field, key): return self.filler.next(key, cast=lambda data: str(data))
    def imagefield_config(self, field, key): return self.filler.next(key, cast=lambda data: str(data))

    def get_key_from_instance_field(self, model_class, field):
        return get_unique_field_name(field)

    def field_fixture_template(self, field_class):
        return '%s_config' % (field_class.__name__.lower(),)

    def field_fixture_factory(self, field_class):
        try:
            fixture = self.field_fixture_template(field_class)
            getattr(self, fixture)
            return fixture
        except AttributeError:
            if len(field_class.__bases__) > 0:
                parent_class = field_class.__bases__[0] # field must not have multiple inheritance
                return self.field_fixture_factory(parent_class)
            else:
                return None

    def new(self, field):
        config = self.field_fixture_factory(field.__class__)
        is_supported_field = config != None
        if is_supported_field:
            key = self.get_key_from_instance_field(field.model, field)
            data = eval('self.%s(field, "%s")' % (config, key,))
        else:
            if field.null:
                data = None # a workaround for versatility
            else:
                raise UnsupportedFieldError(get_unique_field_name(field))
        return data


DATA_FIXTURE = DefaultDataFixture()

class DynamicFixture(object):

    def __init__(self, fill_nullable_fields=True, ignore_fields=[], number_of_laps=1, model_path=[], data_fixture=None, print_errors=True,
                 **kwargs):
        self.fill_nullable_fields = fill_nullable_fields
        self.ignore_fields = ignore_fields
        self.number_of_laps = number_of_laps
        self.model_path = model_path
        if data_fixture is None:
            self.data_fixture = DATA_FIXTURE
        else:
            self.data_fixture = data_fixture
        self.print_errors = print_errors
        self.kwargs = kwargs

    def _process_field_with_customized_fixture(self, field, fixture, persist_dependencies):
        "Set a custom value to a field."
        if isinstance(fixture, DynamicFixture): # DynamicFixture
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
            data = fixture
        return data

    def _process_field_with_default_fixture(self, field, model_class, persist_dependencies):
        "The field has no custom value, so the default behavior of the tool is applied."
        if field.null and not self.fill_nullable_fields:
            return None
        
        if field_has_default_value(field):
            # TODO: deal with auto_now and auto_now_add for DateField
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
                fixture = DynamicFixture(fill_nullable_fields=self.fill_nullable_fields,
                                         ignore_fields=ignore_fields,
                                         number_of_laps=self.number_of_laps,
                                         model_path=next_model_path,
                                         data_fixture=self.data_fixture,
                                         print_errors=self.print_errors)
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
            for i in range(amount):
                next_instance = self.get(next_model)
                try:
                    manytomany_field.add(next_instance)
                except AttributeError: # M2M with trough: ManyRelatedManager
                    next_instance.save()
        elif isinstance(fixture, list) or isinstance(fixture, tuple):
            items = fixture
            for item in items:
                if isinstance(item, DynamicFixture):
                    next_instance = item.get(next_model)
                else:
                    next_instance = item
                try:
                    manytomany_field.add(next_instance)
                except AttributeError: # M2M with trough: ManyRelatedManager
                    next_instance.save()
        else:
            raise InvalidManyToManyConfigurationError('Field: %s' % field.name, fixture)

    def new(self, model_class, persist_dependencies=True, **kwargs):
        "Create an instance filled with data without persist it."
        kwargs.update(self.kwargs)
        instance = model_class()
        if not isinstance(instance, Model):
            raise InvalidModelError(get_unique_model_name(model_class))
        for field in get_fields_from_model(model_class):
            if isinstance(field, AutoField) and 'id' not in kwargs: continue
            if field.name in self.ignore_fields: continue
            if field.name in kwargs:
                config = kwargs[field.name]
                try:
                    data = self._process_field_with_customized_fixture(field, config, persist_dependencies)
                except Exception as e:
                    raise InvalidConfigurationError(get_unique_field_name(field), e)
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
        kwargs.update(self.kwargs)
        instance = self.new(model_class, **kwargs)
        if is_model_abstract(model_class):
            raise InvalidModelError(get_unique_model_name(model_class)), None, sys.exc_info()[2]
        try:
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

