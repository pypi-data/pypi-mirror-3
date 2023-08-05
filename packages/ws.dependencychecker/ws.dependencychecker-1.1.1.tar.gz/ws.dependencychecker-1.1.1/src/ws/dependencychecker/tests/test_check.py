# Copyright (c) 2011 Wolfgang Schnerring
# See also LICENSE.txt

import gocept.testing.mock
import pkg_resources
import unittest
import ws.dependencychecker.check
import zope.component.globalregistry


class CheckerTest(unittest.TestCase, gocept.testing.mock.Assertions):

    def setUp(self):
        # XXX we don't want zope.testing depdency just for this
        zope.component.globalregistry.base.__init__('base', ())
        self.patches = gocept.testing.mock.Patches()
        self.location = self.patches.add(
            'ws.dependencychecker.check.Distribution.location',
            gocept.testing.mock.Property())
        ws.dependencychecker.check.FilePackageMapping()

    def test_smoke(self):
        ws.dependencychecker.parse.PythonFileParser.register()
        self.location.return_value = pkg_resources.resource_filename(
            __name__, 'fixtures')
        checker = ws.dependencychecker.check.Checker('ws.dependencychecker')
        result = list(checker())
        self.assertEqual(1, len(result))
        missing = result[0]
        self.assertTrue(missing['path'].endswith('fixtures/invalid.py'))
        self.assertEqual('nonexistent', missing['package'])
        self.assertEqual('1', missing['line'])
        self.assertEqual('import nonexistent', missing['text'])

    def test_smoke_zcml(self):
        ws.dependencychecker.parse.PythonFileParser.register()
        ws.dependencychecker.parse.ZCMLParser.register()
        self.location.return_value = pkg_resources.resource_filename(
            __name__, 'fixtures')
        checker = ws.dependencychecker.check.Checker('ws.dependencychecker')
        result = list(checker())
        self.assertEqual(2, len(result))
        result = sorted(result, key=lambda x: x['path'])

        missing = result[0]
        self.assertTrue(missing['path'].endswith('fixtures/invalid.py'))

        missing = result[1]
        self.assertTrue(missing['path'].endswith('fixtures/invalid.zcml'))
        self.assertEqual('nozcml', missing['package'])
        self.assertEqual('6', missing['line'])
        self.assertEqual('<include package="nozcml" />', missing['text'])


class NamespaceTest(unittest.TestCase):

    def test_no_namespace_is_left_alone(self):
        mapping = ws.dependencychecker.check.NamespaceMapping({})
        self.assertEqual('foo.bar', mapping('foo.bar'))

    def test_shortens_to_first_name_after_namespace(self):
        mapping = ws.dependencychecker.check.NamespaceMapping({'foo': None})
        self.assertEqual('foo.bar', mapping('foo.bar'))
        self.assertEqual('foo.bar', mapping('foo.bar.baz'))

    def test_nested_namespaces(self):
        mapping = ws.dependencychecker.check.NamespaceMapping(
            {'foo': None, 'foo.bar': None})
        self.assertEqual('foo.bar.baz', mapping('foo.bar.baz'))
        self.assertEqual('foo.bar.baz', mapping('foo.bar.baz.qux'))
