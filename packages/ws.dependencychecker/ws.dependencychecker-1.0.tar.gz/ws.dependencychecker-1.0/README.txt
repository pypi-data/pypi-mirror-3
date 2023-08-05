====================
ws.dependencychecker
====================

This package provides a ``dependencychecker`` script that checks whether an egg
declares all packages it imports in its setup.py.

.. contents:: :depth: 1

Usage
=====

``dependencychecker <package-spec>``

``package-spec`` is a setuptools `requirement specifier`_, for example::

    dependencychecker ws.dependencychecker
    dependencychecker ws.dependencychecker[test]

Although ``dependencychecker`` does not import any files, it needs the package
and its dependencies to be on the ``PYTHONPATH`` so they are accessible via
``pkg_resources.working_set``.

To use ws.dependencychecker within a buildout, use a snippet like this, for
example::

    [depcheck]
    recipe = zc.recipe.egg
    eggs =
        ${test:eggs}
        ws.dependencychecker

.. _`requirement specifier`: http://peak.telecommunity.com/DevCenter/PkgResources#requirements-parsing

Related packages
================

- `importchecker`_ finds import statements that are not used in the code.

.. _`importchecker`: http://pypi.python.org/pypi/importchecker

Development
===========

The source code is available in the mercurial repository at
http://code.wosc.de/hg/public/ws.dependencychecker

Please report any bugs you find to `Wolfgang Schnerring`_.

.. _`Wolfgang Schnerring`: mailto:wosc@wosc.de
