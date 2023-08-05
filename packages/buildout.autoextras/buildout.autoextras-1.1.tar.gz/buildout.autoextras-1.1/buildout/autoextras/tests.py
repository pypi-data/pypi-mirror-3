# -*- coding: utf-8 -*-
import os
import sys
import re
import shutil
import tempfile

import zc.buildout.tests
import zc.buildout.testselectingpython
import zc.buildout.testing
from zope.testing import doctest, renormalizing


os_path_sep = os.path.sep
if os_path_sep == '\\':
    os_path_sep *= 2


def dirname(d, level=1):
    if level == 0:
        return d
    return dirname(os.path.dirname(d), level-1)


def create_setup_py(loc, name, version='1.0', other=''):
    """Create a setup.py."""
    # One would think zc.buildout.testing would provide
    # something to this effect.
    from zc.buildout.testing import write
    write(loc, 'setup.py', """\
from setuptools import setup, find_packages
setup(name='%(name)s', version='%(version)s', zip_safe=False, packages=find_packages(), %(other)s)
""" % dict(name=name, version=version, other=other))
    write(loc, '%s.py' % name, "#\n")

def create_sample_dists(test):
    """Create a few sample eggs for this tests because the ones in
    zc.buildout.tests.create_sample_eggs are inadequate."""
    dest = test.globs['sample_eggs']
    tmp = tempfile.mkdtemp()
    try:
        # Project distribution
        other_info = "extras_require={'test': ['project_testing']}"
        create_setup_py(tmp, name='project', other=other_info)
        zc.buildout.testing.sdist(tmp, dest)
        
        # Project testing distribution
        other_info = "extra_requires={'config': ['project_config_support >=1.0']}"
        create_setup_py(tmp, name='project_testing')
        zc.buildout.testing.sdist(tmp, dest)

        # Project config support distribution
        create_setup_py(tmp, name='project_config_support')
        zc.buildout.testing.sdist(tmp, dest)

    finally:
        shutil.rmtree(tmp)


def sample_dists_setUp(test):
    """Copied from zc.buildout.testing.easy_install_SetUp."""
    zc.buildout.testing.buildoutSetUp(test)
    # ??? Huh?
    sample_eggs = test.globs['tmpdir']('sample_eggs')
    test.globs['sample_eggs'] = sample_eggs
    os.mkdir(os.path.join(sample_eggs, 'index'))
    create_sample_dists(test)

    add_source_dist = zc.buildout.tests.add_source_dist
    add_source_dist(test)
    test.globs['link_server'] = test.globs['start_server'](
        test.globs['sample_eggs'])
    test.globs['update_extdemo'] = lambda : add_source_dist(test, 1.5)
    zc.buildout.testing.install('zc.recipe.egg', test)


def setUp(test):
    # This sets up buildout (zc.buildout.testing.buildoutSetUp) and creates
    # a bunch of sample distributions for use in the tests.
    sample_dists_setUp(test)
    zc.buildout.testing.install_develop('buildout.autoextras', test)


def load_tests(loader, tests, ignore):
    extensions_txt = doctest.DocFileSuite(
        'extension.txt',
        setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
        checker=renormalizing.RENormalizing([
            zc.buildout.testing.normalize_path,
            zc.buildout.testing.normalize_script,
            zc.buildout.testing.normalize_egg_py,
            zc.buildout.tests.normalize_bang,
            (re.compile('zc.buildout(-\S+)?[.]egg(-link)?'),
             'zc.buildout.egg'),
            (re.compile('[-d]  setuptools-[^-]+-'), 'setuptools-X-')
            ])
        )
    tests.addTests(extensions_txt)
    return tests
