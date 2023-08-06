# -*- coding: utf-8 -*-
"""\
Recipe to produce a .pth file.
"""
import os
import sys
import logging

import pkg_resources
import zc.buildout.easy_install

from buildout.recipe.isolation.utils import (
    as_bool, as_list, as_string,
    )

class BaseRecipe(object):
    """A class for a recipe..."""

    # buildout = None
    # name = None
    # options = None
    # links = ()
    # index = None
    # executable = sys.executable

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        opts = self.options = options
        self.logger = logging.getLogger(self.name)
        # Init find-links & index
        l = opts.get('find-links', buildout['buildout'].get('find-links'))
        self.links = as_list(l)
        opts['find-links'] = as_string(self.links)
        self.index = opts.get('index', buildout['buildout'].get('index'))
        opts['index'] = as_string(self.index)
        self.executable = self.options.get('executable', sys.executable)
        opts['executable'] = self.executable

    def install(self):
        raise NotImplementedError

    update = install


class BaseIsolator(BaseRecipe):
    """Base class for isolate a set of distributions."""

    def __init__(self, buildout, name, options):
        super(BaseIsolator, self).__init__(buildout, name, options)

        # Init distribution directories eggs-directory & develop-eggs-directory
        self.eggs_dir = buildout['buildout']['eggs-directory']
        self.develop_eggs_dir = buildout['buildout']['develop-eggs-directory']

        self.dists = as_list(self.options.get('dists', self.name))
        self.options['dists'] = as_string(self.dists)

        # A list to capture artifacts created by this recipe.
        self.artifacts = []

    def _makedirs(self, loc):
        os.makedirs(loc)
        self.artifacts.append(loc)

    def _get_functional_executable(self):
        """Get an executable that exists currently rather than one that may
        exist in the future or in the system we are building for."""
        e = os.path.realpath(self.executable)
        if not os.path.exists(e):
            e = self.buildout['buildout'].get('executable', sys.executable)
        return e

    def working_set(self, dists, extra=()):
        """Separate method to just get the working set."""
        orig_distributions = dists[:]
        dists.extend(extra)
        executable = self._get_functional_executable()
        in_offline_mode = as_bool(self.buildout['buildout'].get('offline'))

        if in_offline_mode:
            ws = zc.buildout.easy_install.working_set(
                dists, executable,
                [self.develop_eggs_dir, self.eggs_dir])
        else:
            always_unzip = as_bool(self.buildout['buildout'].get('unzip'))
            newest = as_bool(self.buildout['buildout'].get('newest'))
            ws = zc.buildout.easy_install.install(
                dists, self.eggs_dir,
                links = self.links,
                index = self.index, 
                executable = executable,
                always_unzip=always_unzip,
                path=[self.develop_eggs_dir],
                newest=newest,
                )
        return orig_distributions, ws

    def install(self):
        return self.artifacts
