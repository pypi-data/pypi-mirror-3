# Copyright (c) 2011 Wolfgang Schnerring
# See also LICENSE.txt

from six.moves import configparser
from six import StringIO
from zope.cachedescriptors.property import Lazy as cachedproperty
import os.path
import pkg_resources
import re
import ws.dependencychecker.parse
import zope.component
import zope.interface
import zope.interface.common.mapping


class Checker(object):

    def __init__(self, package_string, working_set=pkg_resources.working_set):
        self.package_string = package_string
        self.working_set = working_set

    def __call__(self):
        distribution = Distribution(self.package_string, self.working_set)

        for result in self.parse(self.list_files(distribution.location)):
            for row in result:
                dep = row['package']
                if not distribution.depends_on(dep):
                    yield row

    @staticmethod
    def list_files(directory):
        for root, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                yield os.path.join(root, filename)

    def parse(self, files):
        for f in files:
            basename, extension = os.path.splitext(f)
            parser = zope.component.queryUtility(
                ws.dependencychecker.parse.Parser, name=extension)
            if parser:
                yield parser(f)


class Distribution(object):

    def __init__(self, package_string, working_set):
        self.requirement = pkg_resources.Requirement.parse(package_string)
        self.distribution = working_set.resolve([self.requirement])[0]

    def depends_on(self, package):
        for dependency in self.dependencies:
            if package.startswith(dependency):
                return True
        return False

    @property
    def location(self):
        return self.distribution.location

    @cachedproperty
    def dependencies(self):
        result = [self.distribution]
        result.extend(self.distribution.requires(self.requirement.extras))
        result = [x.project_name for x in result]
        result.append('__builtin__')

        mapping = zope.component.getUtility(PackageMapping)
        for package in result:
            additional = mapping.get(package)
            if additional:
                result.extend(additional)

        return sorted(result)


class PackageMapping(zope.interface.common.mapping.IEnumerableMapping):
    pass


class FilePackageMapping(object):

    zope.interface.implements(PackageMapping)

    def __init__(self):
        self.mapping = {}
        self.parse(pkg_resources.resource_filename(__name__, 'modules.cfg'))
        zope.component.getSiteManager().registerUtility(self, PackageMapping)

    def parse(self, filename):
        contents = open(filename).read()
        contents = '\n'.join(filter(None, contents.split('\n')))
        contents = re.sub(
            r'^([^[#]\S*)$', r'\1 = dummy', contents, flags=re.MULTILINE)

        config = configparser.ConfigParser()
        config.optionxform = str
        config.readfp(StringIO(contents))
        for section in config.sections():
            packages = self.mapping.setdefault(section, [])
            packages.extend(x[0] for x in config.items(section))

    def __getattr__(self, name):
        return getattr(self.mapping, name)


class NamespaceMapping(object):

    def __init__(self, namespaces=pkg_resources._namespace_packages):
        # NOTE: _namespace_packages isn't part of the public API
        self.namespaces = list(
            reversed(sorted(filter(None, namespaces.keys()))))

    def __call__(self, package):
        for ns in self.namespaces:
            if package.startswith(ns):
                parts = package.split('.')
                nslen = len(ns.split('.'))
                return '.'.join(parts[:nslen+1])
        return package
