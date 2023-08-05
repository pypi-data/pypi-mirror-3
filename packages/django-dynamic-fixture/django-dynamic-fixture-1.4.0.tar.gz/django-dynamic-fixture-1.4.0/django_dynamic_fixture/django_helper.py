# -*- coding: utf-8 -*-
"""
Module to wrap dirty stuff of django core.
"""
from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.db.models.base import ModelBase


def get_apps(application_labels=[], exclude_application_labels=[]):
    """
    - if not @application_labels and not @exclude_application_labels, it returns all applications.
    - if @application_labels is not None, it returns just these applications, 
    except applications with label in exclude_application_labels.
    """
    if application_labels:
        applications = []
        for app_label in application_labels:
            applications.append(models.get_app(app_label))
    else:
        applications = models.get_apps()
    if exclude_application_labels:
        for app_label in exclude_application_labels:
            if app_label:
                applications.remove(models.get_app(app_label))
    return applications


def get_app_name(app):
    return app.__name__.replace('.models', '')


def get_model_name(model):
    return model.__name__


def get_unique_model_name(model):
    return model.__module__.replace('.models', '') + '.' + model.__name__


def get_unique_field_name(field):
    return get_unique_model_name(field.model) + '.' + field.name


def get_models_of_an_app(app):
    """
    app is the object returned by get_apps method
    """
    return models.get_models(app)


def get_fields_from_model(model_class):
    return model_class._meta.fields


def is_model_class(model_class):
    return model_class.__class__ == ModelBase


def is_model_abstract(model):
    return model._meta.abstract


def is_model_managed(model):
    return model._meta.managed


def get_fields(model):
    return model._meta.local_fields


def get_field_names_from_model(model_class):
    fields = get_fields_from_model(model_class)
    return [field.name for field in fields]


def get_many_to_many_fields_from_model(model_class):
    return model_class._meta.many_to_many


def get_related_model(field):
    return field.rel.to


def field_is_a_parent_link(field):
    return hasattr(field, 'parent_link') and field.parent_link


def field_has_choices(field):
    return bool(len(field.choices) > 0 and field.choices)


def field_has_default_value(field):
    return field.default != NOT_PROVIDED


#def listeners():
#    from django.db.models.signals import pre_save, pre_init, pre_delete, post_save, post_delete, post_init, post_syncdb
#
#    for signal in [pre_save, pre_init, pre_delete, post_save, post_delete, post_init, post_syncdb]:
#        # print a List of connected listeners
#        import pdb; pdb.set_trace()
#        for rec in signal.receivers:
#            print rec
#        print "\n"


def print_field_values(model_instance):
    "Print values from all fields of a model instance."
    if model_instance == None:
        print('\n:: Model Unknown: None')
    else:
        print('\n:: Model %s (%s)' % (model_instance.__class__.__name__, model_instance.id))
        for field in get_fields_from_model(model_instance.__class__):
            print('%s: %s' % (field.name, getattr(model_instance, field.name)))
        if model_instance.id is not None:
            for field in get_many_to_many_fields_from_model(model_instance.__class__):
                print('%s: %s' % (field.name, getattr(model_instance, field.name).all()))
