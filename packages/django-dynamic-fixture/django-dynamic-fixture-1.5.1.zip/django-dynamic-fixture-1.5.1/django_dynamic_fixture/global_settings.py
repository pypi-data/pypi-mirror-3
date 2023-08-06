# -*- coding: utf-8 -*-

"""
Module that contains wrappers and shortcuts.
This is the facade of all features of DDF.
"""
import sys

from django.conf import settings
from django.core.urlresolvers import get_mod_func
from django.utils.importlib import import_module

from django_dynamic_fixture.fixture_algorithms.sequential_fixture import SequentialDataFixture, StaticSequentialDataFixture
from django_dynamic_fixture.fixture_algorithms.random_fixture import RandomDataFixture


class DDFImproperlyConfigured(Exception):
    "DDF is improperly configured. Some global settings has bad value in django settings."


try:
    # It must be 'sequential', 'static_sequential', 'random' or 'path.to.CustomDataFixtureClass'
    # default = SequentialDataFixture()
    INTERNAL_DATA_FIXTURES = {'sequential': SequentialDataFixture(),
                              'static_sequential': StaticSequentialDataFixture(),
                              'random': RandomDataFixture()}
    if hasattr(settings, 'DDF_DEFAULT_DATA_FIXTURE'):
        if settings.DDF_DEFAULT_DATA_FIXTURE in INTERNAL_DATA_FIXTURES.keys():
            DDF_DEFAULT_DATA_FIXTURE = INTERNAL_DATA_FIXTURES[settings.DDF_DEFAULT_DATA_FIXTURE]
        else:
            # path.to.CustomDataFixtureClass
            mod_name, obj_name = get_mod_func(settings.DDF_DEFAULT_DATA_FIXTURE)
            module = import_module(mod_name)
            custom_data_fixture = getattr(module, obj_name)
            DDF_DEFAULT_DATA_FIXTURE = custom_data_fixture()
    else:
        DDF_DEFAULT_DATA_FIXTURE = INTERNAL_DATA_FIXTURES['sequential']
except:
    raise DDFImproperlyConfigured("DDF_DEFAULT_DATA_FIXTURE (%s) must be 'sequential', 'static_sequential', 'random' or 'path.to.CustomDataFixtureClass'." % settings.DDF_DEFAULT_DATA_FIXTURE), None, sys.exc_info()[2]

# DDF_FILL_NULLABLE_FIELDS must be the boolean False, or it will be setted to True.
# default = True
try:
    if hasattr(settings, 'DDF_FILL_NULLABLE_FIELDS') and settings.DDF_FILL_NULLABLE_FIELDS not in [True, False]:
        # to educate users to use this property correctly.
        raise DDFImproperlyConfigured("DDF_FILL_NULLABLE_FIELDS (%s) must be True or False." % settings.DDF_FILL_NULLABLE_FIELDS), None, sys.exc_info()[2]
    DDF_FILL_NULLABLE_FIELDS = settings.DDF_FILL_NULLABLE_FIELDS != False if hasattr(settings, 'DDF_FILL_NULLABLE_FIELDS') else True
except Exception as e:
    raise DDFImproperlyConfigured("DDF_FILL_NULLABLE_FIELDS (%s) must be True or False." % settings.DDF_FILL_NULLABLE_FIELDS), None, sys.exc_info()[2]

try:
    # default = []
    DDF_IGNORE_FIELDS = list(settings.DDF_IGNORE_FIELDS) if hasattr(settings, 'DDF_IGNORE_FIELDS') else []
except Exception as e:
    raise DDFImproperlyConfigured("DDF_IGNORE_FIELDS (%s) must be a list of strings" % settings.DDF_IGNORE_FIELDS), None, sys.exc_info()[2]

try:
    # default = 1
    DDF_NUMBER_OF_LAPS = int(settings.DDF_NUMBER_OF_LAPS) if hasattr(settings, 'DDF_NUMBER_OF_LAPS') else 1
except Exception as e:
    raise DDFImproperlyConfigured("DDF_NUMBER_OF_LAPS (%s) must be a integer number." % settings.DDF_NUMBER_OF_LAPS), None, sys.exc_info()[2]


# DDF_VALIDATE_MODELS must be the boolean False, or it will be setted to True.
# default = False
try:
    if hasattr(settings, 'DDF_VALIDATE_MODELS') and settings.DDF_VALIDATE_MODELS not in [True, False]:
        # to educate users to use this property correctly.
        raise DDFImproperlyConfigured("DDF_VALIDATE_MODELS (%s) must be True or False." % settings.DDF_VALIDATE_MODELS), None, sys.exc_info()[2]
    DDF_VALIDATE_MODELS = settings.DDF_VALIDATE_MODELS != False if hasattr(settings, 'DDF_VALIDATE_MODELS') else False
except Exception as e:
    raise DDFImproperlyConfigured("DDF_VALIDATE_MODELS (%s) must be True or False." % settings.DDF_VALIDATE_MODELS), None, sys.exc_info()[2]


# DDF_VALIDATE_ARGS must be the boolean False, or it will be setted to True.
# default = False
try:
    if hasattr(settings, 'DDF_VALIDATE_ARGS') and settings.DDF_VALIDATE_ARGS not in [True, False]:
        # to educate users to use this property correctly.
        raise DDFImproperlyConfigured("DDF_VALIDATE_ARGS (%s) must be True or False." % settings.DDF_VALIDATE_ARGS), None, sys.exc_info()[2]
    DDF_VALIDATE_ARGS = settings.DDF_VALIDATE_MODELS != False if hasattr(settings, 'DDF_VALIDATE_ARGS') else False
except Exception as e:
    raise DDFImproperlyConfigured("DDF_VALIDATE_ARGS (%s) must be True or False." % settings.DDF_VALIDATE_ARGS), None, sys.exc_info()[2]
