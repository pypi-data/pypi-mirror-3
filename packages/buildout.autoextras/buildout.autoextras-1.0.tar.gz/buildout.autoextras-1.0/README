buildout.autoextras
===================

Buildout (zc.buildout) extension for including setuptools extras_require
options for all items in a target option if the extra exists.

Usage
-----

This is a buildout extension, so simply add it to your extensions list::

    [buildout]
    extensions = buildout.autoextras

Options
-------

There are two options...

autoextra-keys
    A list of extra keys (e.g. test, zcml, etc.) that should be included if
    the package has the extra.

autoextra-targets
    A list of targets to check for the extras. For example, a buildout part
    named ``demo`` that has an ``eggs`` option. The target in this case would
    be ``demo:eggs``. This is similar to zc.buildout's variable replace
    syntax except without the ``${}`` symbolling. 

Together these options might look something like::

    [buildout]
    extensions = buildout.autoextras
    parts = demo
    autoextra-keys = zcml
    autoextra-targets = demo:eggs

    [demo]
    recipe = zc.recipe.eggs
    eggs =
        zope.testing
        zope.i18n
