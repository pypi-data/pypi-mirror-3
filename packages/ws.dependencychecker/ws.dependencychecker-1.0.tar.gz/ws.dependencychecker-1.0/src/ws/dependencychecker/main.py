# Copyright (c) 2011 Wolfgang Schnerring
# See also LICENSE.txt

from ConfigParser import ConfigParser
from StringIO import StringIO
import fnmatch
import os
import os.path
import pkg_resources
import re
import sys


def main():
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: %s package-spec\n' % sys.argv[0])
        raise SystemExit(1)
    package = sys.argv[1]
    check(package)


def check(package):
    requirement = pkg_resources.Requirement.parse(package)
    distribution = pkg_resources.working_set.resolve([requirement])[0]
    available = list_available_packages(distribution, requirement.extras)

    files = [File(x) for x in find(distribution.location, '*.py')]
    for f in files:
        for row in f.list_imports():
            dep = row['package']
            if not prefix_match(dep, available):
                print ':'.join([row['path'], row['line'], row['text']])


def find(directory, pattern):
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)


def list_available_packages(distribution, extras):
    # XXX refactor & test this function
    result = [distribution] + distribution.requires(extras)
    result = [x.project_name for x in result]
    result.append('__builtin__')

    contents = pkg_resources.resource_string(__name__, 'modules.cfg')
    contents = '\n'.join(filter(None, contents.split('\n')))
    contents = re.sub(
        r'^([^[#]\S*)$', r'\1 = dummy', contents, flags=re.MULTILINE)

    config = ConfigParser()
    config.optionxform = str
    config.readfp(StringIO(contents))
    for package in result:
        if not config.has_section(package):
            continue
        result.extend(x[0] for x in config.items(package))
    return sorted(result)


def prefix_match(needle, haystack):
    for package in haystack:
        if needle.startswith(package):
            return True
    return False


class File(object):

    IMPORT = re.compile(r'import +(\S+)')
    FROM_IMPORT = re.compile(r'from +(\S+) +import +\S')

    def __init__(self, path):
        self.path = path

    def list_imports(self):
        result = []
        for i, line in enumerate(open(self.path).readlines()):
            package = self.extract_package(line)
            if package:
                result.append(dict(
                        path=self.path,
                        line=str(i),
                        package=package,
                        text=line.strip()))
        return result

    def extract_package(self, line):
        candidates = [self.extract_from_import(line),
                      self.extract_import(line)]
        candidates = filter(None, candidates)
        if candidates:
            return candidates[0]

    def extract_from_import(self, line):
        match = self.FROM_IMPORT.search(line)
        if match:
            return match.group(1)

    def extract_import(self, line):
        match = self.IMPORT.search(line)
        if match:
            return match.group(1)
