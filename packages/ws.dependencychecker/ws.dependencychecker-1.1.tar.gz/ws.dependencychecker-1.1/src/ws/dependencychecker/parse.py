# Copyright (c) 2011 Wolfgang Schnerring
# See also LICENSE.txt

import re
import zope.interface


class Parser(zope.interface.Interface):

    def __call__(path):
        """Parses the file given by the absolute ``path`` and returns a list of
        files imported by that file. Each list item is a dict with the
        following keys:

        :package: the name of the imported package
        :line: the line number as a string
        :text: the full text of the line
        :path: the absolute path of the file
        """


class ParserBase(object):

    zope.interface.implements(Parser)

    extension = NotImplemented

    def __call__(self, path):
        result = []
        for i, line in enumerate(open(path).readlines()):
            package = self.extract_package(line)
            if package:
                result.append(dict(
                        path=path,
                        line=str(i+1),
                        package=package,
                        text=line.strip()))
        return result

    def extract_package(self, line):
        raise NotImplementedError('override in subclass')

    @classmethod
    def register(cls):
        zope.component.getSiteManager().registerUtility(
            cls(), name=cls.extension)


PACKAGE = '[A-Za-z0-9._]+'


class PythonFileParser(ParserBase):

    extension = '.py'

    IMPORT = re.compile(r'^\s*import\s+(%s).*$' % PACKAGE)
    FROM_IMPORT = re.compile(r'^\s*from\s+(%s)\s+import.*$' % PACKAGE)

    def extract_package(self, line):
        candidates = [self.extract_from_import(line),
                      self.extract_import(line)]
        candidates = list(filter(None, candidates))
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


class ZCMLParser(ParserBase):

    extension = '.zcml'

    INCLUDE_RE = re.compile(r'<include package="([^.]%s)"' % PACKAGE)
    INCLUDE = '<include'
    COMMENT = '<!--'

    def extract_package(self, line):
        match = self.INCLUDE_RE.search(line)
        comment_pos = line.find(self.COMMENT)
        include_pos = line.find(self.INCLUDE)
        if match and (comment_pos == -1 or comment_pos > include_pos):
            return match.group(1)
