# Copyright (c) 2011 Wolfgang Schnerring
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='ws.dependencychecker',
    version='1.1',
    author='Wolfgang Schnerring <wosc at wosc dot de>',
    author_email='wosc@wosc.de',
    url='http://code.wosc.de/hg/public/ws.dependencychecker',
    description="""\
Checks whether imported packages are declared in setup.py
""",
    long_description=(
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL',
    namespace_packages=['ws'],
    install_requires=[
        'plac',
        'setuptools',
        'six',
        'zope.cachedescriptors',
        'zope.component',
        'zope.interface',
    ],
    extras_require=dict(test=[
        'gocept.testing>=1.2.1dev',
        'mock',
    ]),
    entry_points=dict(console_scripts=[
        'dependencychecker = ws.dependencychecker.main:main',
    ]),
)
