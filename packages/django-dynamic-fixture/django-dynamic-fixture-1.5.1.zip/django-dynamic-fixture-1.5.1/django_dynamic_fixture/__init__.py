# -*- coding: utf-8 -*-

"""
This is the facade of all features of DDF.
Module that contains wrappers and shortcuts.
"""

from django_dynamic_fixture.ddf import DynamicFixture
from django_dynamic_fixture.django_helper import print_field_values
from django_dynamic_fixture.fixture_algorithms.sequential_fixture import SequentialDataFixture, \
    StaticSequentialDataFixture
from django_dynamic_fixture.global_settings import DDF_DEFAULT_DATA_FIXTURE, DDF_FILL_NULLABLE_FIELDS, DDF_NUMBER_OF_LAPS, \
                                                    DDF_IGNORE_FIELDS, DDF_VALIDATE_MODELS, DDF_VALIDATE_ARGS


# Wrappers
def new(model, data_fixture=DDF_DEFAULT_DATA_FIXTURE, fill_nullable_fields=DDF_FILL_NULLABLE_FIELDS,
        validate_models=DDF_VALIDATE_MODELS, validate_args=DDF_VALIDATE_ARGS,
        ignore_fields=[], number_of_laps=DDF_NUMBER_OF_LAPS, n=1, print_errors=True, persist_dependencies=True, **kwargs):
    """
    Return one or many valid instances of Django Models with fields filled with auto generated or customized data.
    All instances will NOT be persisted in the database, except its dependencies, in case @persist_dependencies is True.
    
    @data_fixture: override DDF_DEFAULT_DATA_FIXTURE configuration. Default is SequentialDataFixture().
    @fill_nullable_fields: override DDF_FILL_NULLABLE_FIELDS global configuration. Default is True.
    @validate_models: override DDF_VALIDATE_MODELS global configuration. Default is False.
    @validate_args: override DDF_VALIDATE_ARGS global configuration. Default is False.
    @ignore_fields: List of fields that will be ignored by DDF. It will be concatenated with the global list DDF_IGNORE_FIELDS. Default is [].
    @number_of_laps: override DDF_NUMBER_OF_LAPS global configuration. Default 1.
    @n: number of instances to be created with the given configuration. Default is 1.
    @print_errors: print on console all instance values if DDF can not generate a valid object with the given configuration.
    @persist_dependencies: If True, save internal dependencies, otherwise just instantiate them. Default is True.

    Wrapper for the method DynamicFixture.new
    """
    ignore_fields.extend(DDF_IGNORE_FIELDS)
    d = DynamicFixture(data_fixture=data_fixture,
                       fill_nullable_fields=fill_nullable_fields,
                       validate_models=validate_models,
                       validate_args=validate_args,
                       ignore_fields=ignore_fields,
                       number_of_laps=number_of_laps,
                       print_errors=print_errors)
    if n == 1:
        return d.new(model, persist_dependencies=persist_dependencies, **kwargs)
    instances = []
    for _ in range(n):
        instances.append(d.new(model, persist_dependencies=persist_dependencies, **kwargs))
    return instances


def get(model, data_fixture=DDF_DEFAULT_DATA_FIXTURE, fill_nullable_fields=DDF_FILL_NULLABLE_FIELDS,
        validate_models=DDF_VALIDATE_MODELS, validate_args=DDF_VALIDATE_ARGS,
        ignore_fields=[], number_of_laps=DDF_NUMBER_OF_LAPS, n=1, print_errors=True, **kwargs):
    """
    Return one or many valid instances of Django Models with fields filled with auto generated or customized data.
    All instances will be persisted in the database.
    
    @data_fixture: override DDF_DEFAULT_DATA_FIXTURE configuration. Default is SequentialDataFixture().
    @fill_nullable_fields: override DDF_FILL_NULLABLE_FIELDS global configuration. Default is True.
    @validate_models: override DDF_VALIDATE_MODELS global configuration. Default is False.
    @validate_args: override DDF_VALIDATE_ARGS global configuration. Default is False.
    @ignore_fields: List of fields that will be ignored by DDF. It will be concatenated with the global list DDF_IGNORE_FIELDS. Default is [].
    @number_of_laps: override DDF_NUMBER_OF_LAPS global configuration. Default 1.
    @n: number of instances to be created with the given configuration. Default is 1.
    @print_errors: print on console all instance values if DDF can not generate a valid object with the given configuration.

    Wrapper for the method DynamicFixture.get
    """
    ignore_fields.extend(DDF_IGNORE_FIELDS)
    d = DynamicFixture(data_fixture=data_fixture,
                       fill_nullable_fields=fill_nullable_fields,
                       validate_models=validate_models,
                       validate_args=validate_args,
                       ignore_fields=ignore_fields,
                       number_of_laps=number_of_laps,
                       print_errors=print_errors)
    if n == 1:
        return d.get(model, **kwargs)
    instances = []
    for _ in range(n):
        instances.append(d.get(model, **kwargs))
    return instances


# Shortcuts
F = DynamicFixture
N = new
G = get
P = print_field_values
