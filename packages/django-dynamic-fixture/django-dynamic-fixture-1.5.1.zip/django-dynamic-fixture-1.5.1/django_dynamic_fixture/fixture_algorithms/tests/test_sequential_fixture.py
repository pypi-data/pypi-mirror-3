# -*- coding: utf-8 -*-

from django.test import TestCase

from django_dynamic_fixture.fixture_algorithms.tests.abstract_test_generic_fixture import DataFixtureTestCase
from django_dynamic_fixture.fixture_algorithms.sequential_fixture import SequentialDataFixture, StaticSequentialDataFixture

    
class SequentialDataFixtureTestCase(TestCase, DataFixtureTestCase):
    def setUp(self):
        self.fixture = SequentialDataFixture()
        

class StaticSequentialDataFixtureTestCase(TestCase, DataFixtureTestCase):
    def setUp(self):
        self.fixture = StaticSequentialDataFixture()
        
