# -*- coding: utf-8 -*-
"""\
Recipe to produce a .pth file.
"""
import os
import zc.buildout.easy_install
from buildout.recipe.isolation.utils import (
    write_path_file,
    remove_setuptools,
    filter_working_set,
    as_bool, as_list, as_string,
    )
from buildout.recipe.isolation.base import BaseIsolator


class PthProducer(BaseIsolator):
    """Produce a .pth file from the given distribution list."""

    def __init__(self, buildout, name, options):
        super(PthProducer, self).__init__(buildout, name, options)
        self.pth_filename = "%s.pth" % self.name
        self.parts_dir = self.buildout['buildout']['parts-directory']
        self.pth_loc = os.path.join(self.parts_dir, "%s-pth" % self.name)
        self.pth_file_loc = os.path.join(self.pth_loc, self.pth_filename)
        self.options['pth-location'] = as_string(self.pth_loc)
        self.options['pth-file-location'] = as_string(self.pth_file_loc)

        # Handle the distribution exclusion case.
        self.exclude_dists = as_list(self.options.get('exclude-dists'))
        self.options['exclude-dists'] = as_string(self.exclude_dists)

        # Should we remove setuptools/distribute from the isolation?
        # This is a convience setting...
        v = self.options.get('should-remove-setuptools',
                             self.buildout['buildout'].get('should-remove-setuptools',
                                                           False)
                             )
        self.should_remove_setuptools = as_bool(v)
        self.options['should-remove-setuptools'] = as_string(v)

    def _setup_location(self):
        """Set up the location for the .pth file"""
        loc = self.pth_loc
        if not os.path.exists(loc):
            if loc.find(self.parts_dir) >= 0:
                self._makedirs(loc)
                self.artifacts.append(loc)
            else:
                raise RuntimeError("The pth file directory does not exist. "
                                   "You should create it before "
                                   "continuing. Location is %s" % loc)

    def install(self):
        self._setup_location()
        incl_reqs, incl_ws = self.working_set(self.dists)
        excl_reqs, excl_ws = self.working_set(self.exclude_dists)
        working_set = filter_working_set(incl_ws, excl_ws)
        if self.should_remove_setuptools:
            working_set = remove_setuptools(working_set)

        write_path_file(working_set, self.pth_file_loc)
        self.artifacts.append(self.pth_file_loc)
        return super(PthProducer, self).install()
