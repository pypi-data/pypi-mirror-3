# -*- coding: utf-8 -*-
import os
import sys
import shutil
import warnings
import logging

import pkg_resources
import zc.buildout.easy_install

from buildout.recipe.isolation.utils import as_bool, as_list, as_string

default_logger = logging.getLogger('buildout.recipe.isolation')


class Isolate(object):
    """zc.buildout recipe."""

    buildout = None
    name = None
    options = None
    links = ()
    index = None
    created = []

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        # Init find-links & index
        self.links = as_list(options.get('find-links', buildout['buildout'].get('find-links')))
        self.options['find-links'] = as_string(self.links)
        self.index = options.get('index', buildout['buildout'].get('index', None))
        self.options['index'] = as_string(self.index)

        # Init distribution directories eggs-directory & develop-eggs-directory
        self.eggs_dir = buildout['buildout']['eggs-directory']
        self.develop_eggs_dir = buildout['buildout']['develop-eggs-directory']

        self.pth_filename = "%s.pth" % self.name

        self.dists = as_list(self.options.get('dists', self.name))
        self.options['dists'] = as_string(self.dists)

        self.exclude_dists = as_list(self.options.get('exclude-dists', ''))
        self.options['exclude-dists'] = as_string(self.exclude_dists)

        self.parts_dir = self.buildout['buildout']['parts-directory']
        self.default_dir_locs = {'dists_loc': self.name,
                                 'scripts_loc': "%s-scripts" % self.name,
                                 'pth_loc': "%s-pth" % self.name}
        self.default_dir_locs['pth_file_loc'] = os.path.join(self.default_dir_locs['pth_loc'], self.pth_filename)

        # These are complicated enough without adding in the options lookup
        # crap. So one liners are used to confuse the issue even more!
        # *Bitter about using buildout*
        self.dists_loc = self.options.get('dists-location', os.path.join(self.parts_dir, self.default_dir_locs['dists_loc']))
        self.options['dists-location'] = as_string(self.dists_loc)

        self.scripts_loc = self.options.get('scripts-location', os.path.join(self.parts_dir, self.default_dir_locs['scripts_loc']))
        self.options['scripts-location'] = as_string(self.scripts_loc)

        self.pth_loc = self.options.get('pth-location', os.path.join(self.parts_dir, self.default_dir_locs['pth_loc']))
        self.options['pth-location'] = as_string(self.pth_loc)
        self.pth_file_loc = os.path.join(self.pth_loc, self.pth_filename)
        self.options['pth-file-location'] = as_string(self.pth_file_loc)

        self.extra_pth = as_list(self.options.get('extra-pth', [])) 
        self.options['extra-pth'] = as_string(self.extra_pth)

        self.exclude_own_pth = as_bool(self.options.get('exclude-own-pth', False))
        self.options['exclude-own-pth'] = as_string(self.exclude_own_pth)

        self.executable = self.options.get('executable', sys.executable)
        self.options['executable'] = self.executable

        self.staged = as_bool(self.options.get('stage-locally', False))
        self.options['stage-locally'] = as_string(self.staged)

    def __create_location(self, loc):
        os.makedirs(loc)
        self.created.append(loc)

    def _get_staging_location(self, loc):
        if self.staged:
            location = os.path.join(self.parts_dir, self.default_dir_locs[loc])
        else:
            location = getattr(self, loc)
        return location

    def _setup_locs(self):
        """Set up the destination locations for the distribution libraries and
        scripts."""
        for loc_attr in ['dists_loc', 'scripts_loc', 'pth_loc']:
            loc = getattr(self, loc_attr)
            staging_loc = self._get_staging_location(loc_attr)
            if not os.path.exists(loc):
                if self.staged:
                    self.logger.warn("The final destination directory for "
                                     "'%s' does not exist. Location is %s"
                                     % (loc_attr, loc))
                elif loc.find(self.parts_dir) >= 0:
                    self.__create_location(loc)
                else:
                    raise RuntimeError("The '%s' directory does not exist. "
                                       "You should create it before "
                                       "continuing. Location is %s"
                                       % (loc_attr, loc))
            if self.staged and not os.path.exists(staging_loc):
                self.__create_location(staging_loc)

    def _copy_dist(self, dist):
        """Copy a built distribution to a specified destination."""
        target = dist.location
        dist_dirname = os.path.basename(target)
        #: dest and final_dest will match if we aren't in staging mode. See
        # the _get_staging_location for more information.
        dest = os.path.join(self._get_staging_location('dists_loc'), dist_dirname)
        final_dest = os.path.join(self.dists_loc, dist_dirname)
        name = dist.project_name

        if os.path.exists(dest):
            self.logger.info("Distribution %s exists, not updating." % name)
            return final_dest

        if os.path.isdir(target):
            copy = shutil.copytree
        else:
            copy = shutil.copy2

        self.logger.info("Copying %s to the %s directory."
                         % (name, self.staged and 'staging' or 'destination'))
        copy(target, dest)
        return final_dest

    def _get_functional_executable(self):
        executable = os.path.realpath(self.executable)
        if not os.path.exists(executable):
            executable = self.buildout['buildout'].get('executable', sys.executable)
        return executable

    def working_set(self, dists, extra=()):
        """Separate method to just get the working set."""
        distributions = dists
        orig_distributions = distributions[:]
        distributions.extend(extra)
        executable = self._get_functional_executable()

        if as_bool(self.buildout['buildout'].get('offline')):
            ws = zc.buildout.easy_install.working_set(
                distributions, executable,
                [self.develop_eggs_dir, self.eggs_dir])
        else:
            ws = zc.buildout.easy_install.install(
                distributions, self.eggs_dir,
                links = self.links,
                index = self.index, 
                executable = executable,
                always_unzip=as_bool(self.buildout['buildout'].get('unzip', False)),
                path=[self.develop_eggs_dir],
                newest=as_bool(self.buildout['buildout'].get('newest')),
                )

        return orig_distributions, ws

    def get_filtered_working_set(self, in_ws, ex_ws):
        ws = pkg_resources.WorkingSet([])
        excluded_dists = ex_ws.by_key.keys()
        for name, dist in in_ws.by_key.iteritems():
            if name not in excluded_dists:
                ws.add(dist)
        return ws

    def isolate(self, working_set):
        """Given the a list of distributions, we will isolate them in a
        separate directory that has been predefined."""
        dists = [dist for dist in working_set.by_key.values()]

        if self.staged:
            isolation_dir = self._get_staging_location('dists_loc')
            pth_file = self._get_staging_location('pth_file_loc')
        else:
            isolation_dir = self.dists_loc
            pth_file = self.pth_file_loc
        pth_list = []

        for dist in dists:
            path = self._copy_dist(dist)
            pth_list.append(path)

        f = open(pth_file, 'w')
        f.write('\n'.join(pth_list))
        f.close()

    def gen_scripts(self, reqs, ws):
        executable = os.path.realpath(self.executable)
        if not os.path.exists(executable):
            executable = self.executable
            self.logger.warn("Can't find the executable on the filesystem. "
                             "Perhaps this setup is not destine to be used "
                             "on this machine. So we are using the given "
                             "executable value %s as is." % executable)
        dest = self._get_staging_location('scripts_loc')
        final_dest = self.scripts_loc
        scripts = None # place holder
        extra_pths = []

        if not self.exclude_own_pth:
            extra_pths.append(self.pth_file_loc)
        if self.extra_pth is not None:
            extra_pths.extend(self.extra_pth)
        return script_installer(reqs, ws, executable,
            dest, scripts, extra_pths, logger=self.logger)

    def install(self):
        self._setup_locs()

        inclusion_reqs, inclusion_ws = self.working_set(self.dists)
        exclusion_reqs, exclusion_ws = self.working_set(self.exclude_dists)

        ws = self.get_filtered_working_set(inclusion_ws, exclusion_ws)
        self.isolate(ws)
        generated_scripts = self.gen_scripts(inclusion_reqs, ws)

        record = self.created + generated_scripts
        return tuple(set(record))

    update = install


pth_init = """
import sys
def pth_injector(pth_file):
    path_file = open(pth_file, 'r')
    sys.path[0:0] = [line
        for line in path_file.read().split('\\n')
        if line is not None]

pth_files = %(pth_file_list)s
for pth in pth_files:
    pth_injector(pth)
"""

def script_installer(reqs, working_set, executable, dest,
            scripts=None,
            extra_pths=(),
            logger=default_logger,
            ):
    generated = []
    entry_points = []
    requirements = [x[1][0] for x in working_set.entry_keys.items()]

    if isinstance(reqs, str):
        raise TypeError('Expected iterable of requirements or entry points,'
                        ' got string.')

    for req in reqs:
        if req not in requirements:
            requirements.append(req)
    for req in requirements:
        if isinstance(req, str):
            req = pkg_resources.Requirement.parse(req)
            dist = working_set.find(req)
            for name in pkg_resources.get_entry_map(dist, 'console_scripts'):
                entry_point = dist.get_entry_info('console_scripts', name)
                entry_points.append(
                    (name, entry_point.module_name,
                     '.'.join(entry_point.attrs))
                    )
        else:
            entry_points.append(req)

    if extra_pths:
        initialization = pth_init % dict(pth_file_list=str(extra_pths))
    else:
        initialization = '\n'

    for name, module_name, attrs in entry_points:
        if name.startswith('easy_install'):
            continue
        if scripts is not None:
            sname = scripts.get(name)
            if sname is None:
                continue
        else:
            sname = name

        sname = os.path.join(dest, sname)
        generated.extend(
            _script(module_name, attrs,
                sname, executable, '',
                initialization, logger=logger)
            )

    return generated


def _script(module_name, attrs, dest, executable, arguments,
            initialization, logger=default_logger):
    generated = []
    script = dest
    if zc.buildout.easy_install.is_win32:
        dest += '-script.py'

    contents = script_template % dict(
        python = zc.buildout.easy_install._safe_arg(executable),
        dash_S = '',
        module_name = module_name,
        attrs = attrs,
        arguments = arguments,
        initialization = initialization,
        )
    changed = not (os.path.exists(dest) and open(dest).read() == contents)

    if zc.buildout.easy_install.is_win32:
        # generate exe file and give the script a magic name:
        exe = script+'.exe'
        new_data = pkg_resources.resource_string('setuptools', 'cli.exe')
        if not os.path.exists(exe) or (open(exe, 'rb').read() != new_data):
            # Only write it if it's different.
            open(exe, 'wb').write(new_data)
        generated.append(exe)

    if changed:
        open(dest, 'w').write(contents)
        logger.info("Generated script %r.", script)

        try:
            os.chmod(dest, 0755)
        except (AttributeError, os.error):
            pass

    generated.append(dest)
    return generated

script_template = zc.buildout.easy_install.script_header + """\

%(initialization)s
import %(module_name)s

if __name__ == '__main__':
    %(module_name)s.%(attrs)s(%(arguments)s)
"""

