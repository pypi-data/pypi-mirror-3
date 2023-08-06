# -*- coding: utf-8 -*-

from django_dynamic_fixture.ddf import DynamicFixture
from django_dynamic_fixture.django_helper import print_field_values


# Wrappers
def new(model, fill_nullable_fields=True, ignore_fields=[], number_of_laps=1, persist_dependencies=True, print_errors=True, n=1, **kwargs):
    "Wrapper for the method DynamicFixture.new"
    d = DynamicFixture(fill_nullable_fields, ignore_fields, number_of_laps, print_errors=print_errors)
    if n == 1:
        return d.new(model, persist_dependencies=persist_dependencies, **kwargs)
    list = []
    for i in range(n):
        list.append(d.new(model, persist_dependencies=persist_dependencies, **kwargs))
    return list


def get(model, fill_nullable_fields=True, ignore_fields=[], number_of_laps=1, print_errors=True, n=1, **kwargs):
    "Wrapper for the method DynamicFixture.get"
    d = DynamicFixture(fill_nullable_fields, ignore_fields, number_of_laps, print_errors=print_errors)
    if n == 1:
        return d.get(model, **kwargs)
    list = []
    for i in range(n):
        list.append(d.get(model, **kwargs))
    return list


F = DynamicFixture
N = new
G = get
P = print_field_values
