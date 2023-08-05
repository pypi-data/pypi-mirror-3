# Copyright (c) 2011 Wolfgang Schnerring
# See also LICENSE.txt

import plac
import ws.dependencychecker.check
import ws.dependencychecker.parse


def main():
    plac.call(_main)


@plac.annotations(
    package=('setuptools requirement string, '
    'e.g. ws.dependencychecker or ws.dependencychecker[test]'),
    verbose=('Print all lines importing missing packages', 'flag', 'v'),
    zcml=('Scan ZCML files', 'flag', 'z'),
    mapping=('Filename with additional egg-->packages mappings', 'option', 'm')
    )
def _main(package, verbose, zcml, mapping=''):
    """Checks whether imported packages are declared in setup.py."""
    ws.dependencychecker.parse.PythonFileParser.register()
    if zcml:
        ws.dependencychecker.parse.ZCMLParser.register()
    mapper = ws.dependencychecker.check.FilePackageMapping()
    if mapping:
        mapper.parse(mapping)
    checker = ws.dependencychecker.check.Checker(package)
    formatter = format_verbose if verbose else format_default
    print formatter(checker())


def format_default(packages):
    map_to_egg = ws.dependencychecker.check.NamespaceMapping()
    packages = set(map_to_egg(x['package']) for x in packages)
    return '\n'.join(sorted(["'%s'," % x for x in packages]))


def format_verbose(packages):
    output = []
    for missing in packages:
        output.append(
            ':'.join([missing['path'], missing['line'], missing['text']]))
    return '\n'.join(output)
