# -*- coding: utf-8 -*-

from django.db import models

from datetime import datetime, date
from decimal import Decimal


class DataFixtureTestCase(object):
    def setUp(self):
        self.fixture = None

    def test_numbers(self):
        self.assertTrue(isinstance(self.fixture.new(models.IntegerField()), int))
        self.assertTrue(isinstance(self.fixture.new(models.SmallIntegerField()), int))
        self.assertTrue(isinstance(self.fixture.new(models.PositiveIntegerField()), int))
        self.assertTrue(isinstance(self.fixture.new(models.PositiveSmallIntegerField()), int))
        self.assertTrue(isinstance(self.fixture.new(models.BigIntegerField()), int))
        self.assertTrue(isinstance(self.fixture.new(models.FloatField()), float))
        self.assertTrue(isinstance(self.fixture.new(models.DecimalField(max_digits=1, decimal_places=1)), Decimal))

    def test_strings(self):
        self.assertTrue(isinstance(self.fixture.new(models.CharField(max_length=1)), unicode))
        self.assertTrue(isinstance(self.fixture.new(models.TextField()), unicode))
        self.assertTrue(isinstance(self.fixture.new(models.SlugField(max_length=1)), unicode))
        self.assertTrue(isinstance(self.fixture.new(models.CommaSeparatedIntegerField(max_length=1)), unicode))
        
    def test_boolean(self):
        self.assertTrue(isinstance(self.fixture.new(models.BooleanField()), bool))
        value = self.fixture.new(models.NullBooleanField())
        self.assertTrue(isinstance(value, bool) or value == None)
    
    def test_date_time_related(self):
        self.assertTrue(isinstance(self.fixture.new(models.DateField()), date))
        self.assertTrue(isinstance(self.fixture.new(models.TimeField()), datetime))
        self.assertTrue(isinstance(self.fixture.new(models.DateTimeField()), datetime))
    
    def test_formatted_strings(self):
        self.assertTrue(isinstance(self.fixture.new(models.EmailField(max_length=100)), unicode))
        self.assertTrue(isinstance(self.fixture.new(models.URLField(max_length=100)), unicode))
        self.assertTrue(isinstance(self.fixture.new(models.IPAddressField(max_length=100)), unicode))
        self.assertTrue(isinstance(self.fixture.new(models.XMLField(max_length=100)), unicode))
    
    def test_files(self):
        self.assertTrue(isinstance(self.fixture.new(models.FilePathField(max_length=100)), unicode))
        self.assertTrue(isinstance(self.fixture.new(models.FileField()), unicode))
        try:
            import pil
            # just test it if the PIL package is installed
            self.assertTrue(isinstance(self.fixture.new(models.ImageField(max_length=100)), unicode))
        except ImportError:
            pass
        
