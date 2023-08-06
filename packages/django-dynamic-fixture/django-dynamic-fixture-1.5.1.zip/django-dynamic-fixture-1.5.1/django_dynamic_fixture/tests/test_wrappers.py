# -*- coding: utf-8 -*-

from django.test import TestCase

from django.db import models
from django.db import IntegrityError

from datetime import datetime, time, date
from decimal import Decimal

from django_dynamic_fixture.models import *
from django_dynamic_fixture import *
from django_dynamic_fixture.ddf import *


class ShortcutsTest(TestCase):
    def test_shortcuts(self):
        new(EmptyModel)
        get(EmptyModel)
        N(EmptyModel)
        G(EmptyModel)
        self.assertTrue(isinstance(F(), DynamicFixture))
        P(new(EmptyModel))


class CreatingMultipleObjectsTest(TestCase):

    def test_new(self):
        self.assertEquals([], new(EmptyModel, n=0))
        self.assertEquals([], new(EmptyModel, n= -1))
        self.assertTrue(isinstance(new(EmptyModel), EmptyModel)) # default is 1
        self.assertTrue(isinstance(new(EmptyModel, n=1), EmptyModel))
        self.assertEquals(2, len(new(EmptyModel, n=2)))

    def test_get(self):
        self.assertEquals([], get(EmptyModel, n=0))
        self.assertEquals([], get(EmptyModel, n= -1))
        self.assertTrue(isinstance(get(EmptyModel), EmptyModel)) # default is 1
        self.assertTrue(isinstance(get(EmptyModel, n=1), EmptyModel))
        self.assertEquals(2, len(get(EmptyModel, n=2)))
