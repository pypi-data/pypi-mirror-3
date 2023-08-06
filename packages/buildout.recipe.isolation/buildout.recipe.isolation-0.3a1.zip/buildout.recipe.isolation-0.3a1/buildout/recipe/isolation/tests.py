# -*- coding: utf-8 -*-
import os
import sys
import re
import shutil
import unittest

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

def sample_eggs_setUp(test):
    """Copied from zc.buildout.testing.easy_install_SetUp."""
    zc.buildout.testing.buildoutSetUp(test)
    sample_eggs = test.globs['tmpdir']('sample_eggs')
    test.globs['sample_eggs'] = sample_eggs
    os.mkdir(os.path.join(sample_eggs, 'index'))
    zc.buildout.tests.create_sample_eggs(test)
    add_source_dist = zc.buildout.tests.add_source_dist
    add_source_dist(test)
    test.globs['link_server'] = test.globs['start_server'](
        test.globs['sample_eggs'])
    test.globs['update_extdemo'] = lambda : add_source_dist(test, 1.5)
    # zc.buildout.testing.install('zc.recipe.egg', test)

def setUp(test):
    # This sets up buildout (zc.buildout.testing.buildoutSetUp) and creates
    # a bunch of sample distributions for use in the tests.
    sample_eggs_setUp(test)
    # 
    zc.buildout.testing.install_develop('buildout.recipe.isolation', test)

def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
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
            ),
        # Add another doctest here...
        ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')