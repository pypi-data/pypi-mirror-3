# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import connection

from nose.plugins import Plugin


class Queries(Plugin):
    name = 'queries'
    _queries_by_test_methods = []

    def configure(self, options, conf):
        Plugin.configure(self, options, conf)
        connection.use_debug_cursor = True

    def beforeTest(self, test):
        self.initial_amount_of_queries = len(connection.queries)

    def afterTest(self, test):
        self.final_amount_of_queries = len(connection.queries)
        self._queries_by_test_methods.append((test, self.final_amount_of_queries - self.initial_amount_of_queries))

    def report(self, stream):
        """Called after all error output has been printed. Print your
        plugin's report to the provided stream. Return None to allow
        other plugins to print reports, any other value to stop them.

        :param stream: stream object; send your output here
        :type stream: file-like object
        """
        stream.write('\nREPORT OF AMOUNT OF QUERIES BY TEST:\n')
        for x in self._queries_by_test_methods:
            testcase = x[0]
            queries = x[1]
            stream.write('\n%s: %s' % (testcase, queries))
        stream.write('\n')
