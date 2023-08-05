# Copyright (c) 2011 Wolfgang Schnerring
# See also LICENSE.txt

import unittest
import ws.dependencychecker.parse


class PythonFileParserTest(unittest.TestCase):

    def extract(self, line):
        return ws.dependencychecker.parse.PythonFileParser().extract_package(
            line)

    def test_recognizes_plain_import(self):
        self.assertEqual('foo', self.extract('import foo'))

    def test_recognizes_plain_import_inside_method(self):
        self.assertEqual('foo', self.extract('  import foo'))

    def test_ignores_imports_within_statements(self):
        self.assertFalse(self.extract('bla(import foo)'))
        self.assertFalse(self.extract("self.assertEqual('import foo', res)"))

    def test_ignores_commented_out_import(self):
        self.assertFalse(self.extract('# import foo'))

    def test_recognizes_import_with_comment(self):
        self.assertEqual('foo', self.extract('import foo # bar'))

    def test_recognizes_from_import(self):
        self.assertEqual('foo', self.extract('from foo import Bar'))

    def test_recognizes_from_import_inside_method(self):
        self.assertEqual('foo', self.extract('  from foo import Bar'))

    def test_ignores_from_imports_within_statements(self):
        self.assertFalse(self.extract('bla(from foo import Bar)'))
        self.assertFalse(
            self.extract("self.assertEqual('from foo import Bar', res)"))

    def test_recognizes_multiple_from_imports(self):
        self.assertEqual('foo', self.extract('from foo import Bar, Baz'))

    def test_ignores_multiple_imports_on_single_line(self):
        # this is a known limitation, but this is frowned upon by PEP 8 anyway
        self.assertEqual('foo', self.extract('import foo, bar'))


class ZCMLParserTest(unittest.TestCase):

    def extract(self, line):
        return ws.dependencychecker.parse.ZCMLParser().extract_package(line)

    def test_recognizes_include(self):
        self.assertEqual('foo', self.extract('<include package="foo" />'))

    def test_ignores_relative_include(self):
        self.assertFalse(self.extract('<include package=".foo" />'))

    def test_ignores_commented_out_include(self):
        self.assertFalse(self.extract('<!-- <include package="foo" /> -->'))

    def test_recognizes_include_with_comment(self):
        self.assertEqual(
            'foo', self.extract('<include package="foo" /> <!-- bar -->'))
