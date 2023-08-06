.. contents::

This buildout recipe's original purpose was to isolate distribution packages and
there dependencies. This recipe was originally developed to be used in the
packaging of Zope2 for the Debian operating system. The recipe can additionally
be used to populate a Python enviroment (or virtual environment). This can be
handy in situations where buildout is required to build the application, but
the developer/system administrator wants to use the application in a typical
Python environment.

The `buildout.recipe.isolation` package contains two recipes
that can be used to isolate distributions and
their dependencies in a single directory.

Path File Producer (pth)
========================

The path file producer recipe is used to produce ``.pth`` files that are in
turn used by Python's ``site`` module during Python startup. See the site
module's documentation for more detail.

An example usage for this recipe might be to isolate
an application's packages separate from it's add-ons.
If you don't know why this is useful, then you may be a lost cause.
The basic premise is to separate the system into managable pieces.
And really, buildout is the wrong tool for the job,
but in some cases we are stuck with it.

Options
-------

dists (optional)
    A list of distributions to isolate.
    These should be listed as one or more setuptools requirement strings.
    Each requirements string should be given on a separate line.
    The part name will act as the default value.

exclude-dists (optional)
    A list of distributions that should be excluded from the isolation.

should-remove-setuptools (optional)
    A convience setting to exclude setuptools (or distribute) from the
    isolation. The value for this setting is false by default.

.. _pth_location_opt:

pth-location (optional)
    A directory location where a `.pth` file will be created for this isolation.
    This option defaults to a location in the buildout parts directory under
    the part (or section) name followed by '-pth' (e.g. for a part named
    `isolated` the default parts directory name would be `isolated-pth`).

    __ pth_file_location_opt_

    The final name of the pth file will be the part name with a `.pth`
    extension. To reference the resulting `.pth` file, use the
    `pth-file-location`__ options.

.. _pth_file_location_opt:

pth-file-location (reference only)
    A location where the `.pth` file lives. The resulting `.pth` file is used
    during the script generation process to provide a list of distributions
    that are isolated somewhere else on the filesystem.

Recipe deliverables
-------------------

- A directory that contains a `.pth` file, which lists the absolute path
  for each package in the isolation context.

How it works
------------

A simple use case for this recipe is building a hybrid application using some
OS packaged Python packages and obtaining the rest using
a buildout configuration.

Let's say want to build a script that uses the ``demo`` package (a faux
package created strictly for this test). And the author of the demo package
has kindly supplied a buildout configuration and version pinnings
for the package dependencies. You'd like to use buildout to build the package,
but not maintain the scripts.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """\
    ... [buildout]
    ... parts = demo
    ...
    ... [demo]
    ... recipe = buildout.recipe.isolation:pth
    ... dists = demo<0.3
    ... find-links = %(server)s
    ... index = %(server)s/index
    ... """ % dict(server=link_server))
    >>> import os
    >>> print system(buildout), #doctest: +ELLIPSIS
    Installing demo.
    Getting distribution for 'demo<0.3'.
    Got demo 0.2.
    Getting distribution for 'demoneeded'.
    Got demoneeded 1.2c1.

Now if we look in the parts directory we'll see a ``demo-pth`` directory.
And inside the directory is our newly created pth file containing the list
of distributions.

    >>> ls(sample_buildout, 'parts')
    d  buildout
    d  demo-pth
    >>> cat(sample_buildout, 'parts/demo-pth', 'demo.pth')
    /sample-buildout/eggs/demo-0.2-py2.6.egg
    /sample-buildout/eggs/demoneeded-1.2c1-py2.6.egg

And if you wanted to use this pth file in a script, you might do something
like the following. (Please note that demo is a fake package, so we won't
actually run the script.)

    >>> write(sample_buildout, 'demo-script.py',
    ... """\
    ... import os
    ... import site
    ...	import demo
    ... 
    ... here = os.path.abspath(os.path.dirname(__file__))
    ... demo_pth_dir = os.path.join(here, 'parts', 'demo-pth')
    ... site.addsitedir(demo_pth_dir)
    ... 
    ... def main():
    ...     demo.prepare(os.curdir)
    ...     resources = demo.find_resources()
    ...     demo.utilize(resources)
    ...     demo.main()
    ... 
    ... if __name__ == '__main__':
    ...     main()
    ... """)

How dependency exclusion works
------------------------------

In some scenarios, you may want to exclude dependencies from being included.
in the isolation. For example, if you have fulfilled some of the dependency requirements at the OS level through the OS's packaging system. Or maybe you've built part of the application in another build but want to extend the application with this one.

Let's create another buildout configuration based on the previous one. This
configuration is setup to isolate the ``bigdemo`` distribution and its
dependencies, but exclude the ``demoneeded`` dependency.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     bigdemo
    ... find-links = %(server)s
    ... index = %(server)s/index
    ...
    ... [bigdemo]
    ... recipe = buildout.recipe.isolation:pth
    ... exclude-dists = demoneeded
    ... """ % dict(server=link_server))
    >>> print system(buildout), #doctest: +ELLIPSIS
    Uninstalling demo.
    Installing bigdemo.
    Getting distribution for 'bigdemo'.
    Got bigdemo 0.1.
    Getting distribution for 'demo'.
    Got demo 0.4c1.

.. note:: In this configuration we changed a few things. One, we put the
   ``index`` and ``find-links`` options in the buildout part, which will be
   used in the bigdemo part as defaults. Two, we left out the ``dists``
   option, which defaults to the part name. This behavior is very similar to
   how zc.recipe.egg works.

And let's have a look at the pth file. As you can see the demoneeded package
is not in the list of distributions.

    >>> cat(sample_buildout, 'parts/bigdemo-pth', 'bigdemo.pth')
    /sample-buildout/eggs/demo-0.4c1-py2.6.egg
    /sample-buildout/eggs/bigdemo-0.1-py2.6.egg

OS packaging isolation
======================

Options
-------

dists
    A list of distributions to isolate given as one or more setuptools
    requirement strings. Each requirements string should be given on a
    separate line. The default is to use the part name as the distribution.

dists-location (optional)
    A directory location where the isolated distributions should be put.
    This option
    defaults to a location in the buildout parts directory under the section
    name where the recipe is being used.

scripts-location (optional)
    A directory location where the distribution scripts should be isolated.
    This option defaults to a location in the buildout parts directory under
    the part (or section) name followed by '-scripts' (e.g. for a part
    named *isolated* the default scripts directory name would be
    `isolated-scripts`).

pth-location (optional)
    A directory location where a `.pth` file will be created for this isolation.
    This option defaults to a location in the buildout parts directory under
    the part (or section) name followed by '-pth' (e.g. for a part named
    *isolated*, the default pth directory name would be `isolated-pth`).

    __ pth_file_location_opt_

    The final name of the pth file will be the part name with a `.pth`
    extension. To reference the resulting `.pth` file, use the
    `pth-file-location`__ options.

pth-file-location (reference only)
    A location where the `.pth` file lives. The resulting `.pth` file is used
    during the script generation process to provide a list of distributions
    that are isolated somewhere else on the filesystem.

extra-pth (optional)
    A list of `.pth` files to include as part of the script initialization.

    This option resolves dependency issues caused by dependency isolation.
    For instance, if you are using `exclude-dists` and those distributions
    that are being exluded are required to run a script, you probably want
    to include the `.pth` file with locations to those dependencies.

exclude-own-pth (optional)
    A boolean option, that when set will exclude the in context part's generated
    `.pth` file from inclusion in scripts. This option is closely tied to
    pth-file-location and extra-pth. This option is false by default.

    The reason this option has been included is because the locations in the
    `.pth` file main already be included in the python path via the `.pth`
    file's location in site-packages.

executable (optional)
    The location of the Python executable. By default this is `sys.executable`.
    
    The executable specified is not executed in the recipe. The location is
    used as the shebang line during the scripts generation.

.. _stage_locally_opt:

stage-locally (optional)
    A boolean option to specify whether we should stage the resources or
    put them in there final destination. If this option is true, the values
    specified for `dist-location`, `script-location` and `pth-location` are
    used to generate the resources, but the resources are placed in
    the default parts locations. This option is handy for staged installation.

Recipe deliverables
-------------------

- A directory that contains a specified distribution(s) package and its
  dependency package(s).
- A directory that contains a `.pth` file, which lists the absolute path
  for each package in the isolation context.
- A directory that contains the scripts that have been generated from the
  distribution(s) package and its dependency packages.

How it works
------------

We have a sample buildout.  Let's update it's configuration file to
install the demo package.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = demo
    ...
    ... [demo]
    ... recipe = buildout.recipe.isolation
    ... dists = demo<0.3
    ... find-links = %(server)s
    ... index = %(server)s/index
    ... """ % dict(server=link_server))

In this example, we limited ourselves to revisions before 0.3. We also
specified where to find distributions using the find-links option.

In order to control the distribution test data, we decided to use buildout's
testing index, shown below::

    >>> print get(link_server),
    <html><body>
    <a href="bigdemo-0.1-py2.3.egg">bigdemo-0.1-pyN.N.egg</a><br>
    <a href="demo-0.1-py2.3.egg">demo-0.1-py2.3.egg</a><br>
    <a href="demo-0.2-py2.3.egg">demo-0.2-py2.3.egg</a><br>
    <a href="demo-0.3-py2.3.egg">demo-0.3-py2.3.egg</a><br>
    <a href="demo-0.4c1-py2.3.egg">demo-0.4c1-py2.3.egg</a><br>
    <a href="demoneeded-1.0.zip">demoneeded-1.0.zip</a><br>
    <a href="demoneeded-1.1.zip">demoneeded-1.1.zip</a><br>
    <a href="demoneeded-1.2c1.zip">demoneeded-1.2c1.zip</a><br>
    <a href="extdemo-1.4.zip">extdemo-1.4.zip</a><br>
    <a href="index/">index/</a><br>
    <a href="other-1.0-py2.3.egg">other-1.0-py2.3.egg</a><br>
    </body></html>

We will be using this index through the testing structure and further
explaining the relationships before each of these distributions.

Let's run the buildout::

    >>> import os
    >>> print system(buildout), #doctest: +ELLIPSIS
    Uninstalling bigdemo.
    Installing demo.
    demo: Copying demo to the destination directory.
    demo: Copying demoneeded to the destination directory.
    demo: Generated script '/sample-buildout/parts/demo-scripts/demo'.

Now, if we look at the buildout parts directory for the isolation::

    >>> ls(sample_buildout, 'parts/demo')
    -  demo-0.2-py2.3.egg
    d  demoneeded-1.2c1-py2.3.egg

These distributions have been entered into a `.pth` file as well. This file
is not directly useful to the buildout, but has it's place in a Python
environment. The contents of the `.pth` file will be the absolute path for each
of the distributions that have been installed into the isolation. Let's have
a look::

    >>> cat(sample_buildout, 'parts/demo-pth', 'demo.pth')
    /sample-buildout/parts/demo/demo-0.2-py2.6.egg
    /sample-buildout/parts/demo/demoneeded-1.2c1-py2.6.egg

__ pth_file_location_opt_

By default the name of the `.pth` files will be the name of the buildout
section, which in this case is demo. You can change the location of the
`.pth` file using the `pth-file-location`__ option.

.. note:: When using the `pth-file-location` option, the directory that the
   `.pth` file will reside, must exist prior to running the buildout.
   If directory  does not exist, an `IOError` will be raised and the
   buildout will fail.

Script generation
-----------------

Some distributions supply command-line scripts with there packages. Buildout
typically generates these scripts for us, because it needs to supply the built
packages to to script. It does this by injecting the distribution locations
into the Python system path. In some cases we do not want to inject anything
into the Python system path, because we may have deposited the generated .pth
file in a virtual environment's site-packages directory. While in other cases,
we might want to supply our .pth file as a mean for import resolution. Let's
take a closer look at both cases.

For the general case, we will likely want to supply our .pth file to the
script. Additionally, we will probably want to supply any .pth files that
dependent isolations may have generated. Here is an example.

    >>> import sys
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     demoneeded
    ...     demo
    ... find-links = %(server)s
    ... index = %(server)s/index
    ...
    ... [demoneeded]
    ... recipe = buildout.recipe.isolation
    ... dists = demoneeded
    ...
    ... [demo]
    ... recipe = buildout.recipe.isolation
    ... dists = bigdemo
    ... exclude-dists = ${demoneeded:dists}
    ... extra-pth = ${demoneeded:pth-file-location}
    ... executable = %(python)s
    ... """ % dict(server=link_server, python=sys.executable))
    >>> print system(buildout), #doctest: +ELLIPSIS
    Uninstalling demo.
    Installing demoneeded.
    demoneeded: Copying demoneeded to the destination directory.
    Installing demo.
    demo: Copying demo to the destination directory.
    demo: Copying bigdemo to the destination directory.
    demo: Generated script '/sample-buildout/parts/demo-scripts/demo'.

The resulting script should have two .pth files in it. The demo.pth file has
been defined and generated from the recipe in context. The demoneeded.pth file
was generated by the demoneeded section and pulled in using the extra-pth
recipe option.

    >>> if sys.platform == 'win32':
    ...    script_name = 'demo-script.py'
    ... else:
    ...    script_name = 'demo'
    >>> script_dir = 'parts/demo-scripts'
    >>> f = open(os.path.join(sample_buildout, script_dir, script_name))
    >>> shebang = f.readline().strip()
    >>> if shebang[:3] == '#!"' and shebang[-1] == '"':
    ...     shebang = '#!'+shebang[3:-1]
    >>> shebang == '#!' + os.path.realpath(sys.executable)
    True
    >>> print f.read(), # doctest: +NORMALIZE_WHITESPACE
    <BLANKLINE>
    import sys
    def pth_injector(pth_file):
        path_file = open(pth_file, 'r')
        sys.path[0:0] = [line
            for line in path_file.read().split('\n')
            if line is not None]
    <BLANKLINE>
    pth_files = ['/sample-buildout/parts/demo-pth/demo.pth', '/sample-buildout/parts/demoneeded-pth/demoneeded.pth']
    for pth in pth_files:
        pth_injector(pth)
    <BLANKLINE>
    import eggrecipedemo
    <BLANKLINE>
    if __name__ == '__main__':
        eggrecipedemo.main()
    >>> f.close()

The second case is where we have deposited the .pth files into a virtual
environment. Let's setup a *fake* virtual environment structure inside the
buildout structure for demonstration sake.

    >>> virtenv = os.path.join(sample_buildout, 'virtenv')
    >>> mkdir(virtenv)
    >>> mkdir(virtenv, 'bin')
    >>> mkdir(virtenv, 'lib')
    >>> mkdir(virtenv, 'lib', 'python2.6')
    >>> mkdir(virtenv, 'lib', 'python2.6', 'site-packages')
    >>> site_pkgs = os.path.join(virtenv, 'lib', 'python2.6', 'site-packages')

All we really need for the purpose of this demonstration is the site-packages
directory.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     demoneeded
    ...     demo
    ... find-links = %(server)s
    ... index = %(server)s/index
    ...
    ... [demoneeded]
    ... recipe = buildout.recipe.isolation
    ... dists = demoneeded
    ... pth-file-location = %(site_pkgs)s
    ...
    ... [demo]
    ... recipe = buildout.recipe.isolation
    ... dists = bigdemo
    ... exclude-dists = ${demoneeded:dists}
    ... pth-file-location = %(site_pkgs)s
    ... exclude-own-pth = trUE
    ... python = %(python)s
    ... """ % dict(server=link_server, python=sys.executable,
    ...     site_pkgs=site_pkgs))
    >>> print system(buildout), #doctest: +ELLIPSIS
    Uninstalling demo.
    Uninstalling demoneeded.
    Installing demoneeded.
    demoneeded: Copying demoneeded to the destination directory.
    Installing demo.
    demo: Copying demo to the destination directory.
    demo: Copying bigdemo to the destination directory.
    demo: Generated script '/sample-buildout/parts/demo-scripts/demo'.

Now if we print out the demo script, we'll find no mention of the .pth files.

    >>> f = open(os.path.join(sample_buildout, script_dir, script_name))
    >>> shebang = f.readline().strip()
    >>> if shebang[:3] == '#!"' and shebang[-1] == '"':
    ...     shebang = '#!'+shebang[3:-1]
    >>> shebang == '#!' + os.path.realpath(sys.executable)
    True
    >>> print f.read(), # doctest: +NORMALIZE_WHITESPACE
    <BLANKLINE>
    import eggrecipedemo
    <BLANKLINE>
    if __name__ == '__main__':
        eggrecipedemo.main()
    >>> f.close()

Why does this work? If we were to use the virtual environments Python
executable, it would load the site-packages directory and any .pth files in
it. This would in turn load the modules we built using the buildout.

.. note:: We aren't actually using the virtual environments Python executable
   in this test case, but it is a simple matter of changing the executable
   value in the system_python section of this buildout.cfg.

Staging the isolation
---------------------

__ stage_locally_opt_

In some situations it is handy to build the packages locally before
transfering these resources to a final destination. To do this we stage the
isolation process with the `stage-locally`__ option.

This option will allow you to set the `dists-location`, `scripts-location` and
`pth-file-location` as final destinations, but place the results in their
default build location. The default build location, if you recall, is in the
buildout's parts directory.

.. note:: The following example isn't necessarily useful beyond the test that
   it satisfies. If you're trying to figure out how to use the staging parts
   of this recipe and run into issues or parts you don't understand, please
   feel free to contact the author (see the package metadata for the address).

Let's have a look at how this works by creating similar buildout to those about
execept now we are setting the `stage-locally` option to `true`::


    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     demo
    ... find-links = %(server)s
    ... index = %(server)s/index
    ...
    ... [demo]
    ... recipe = buildout.recipe.isolation
    ... dists = bigdemo
    ... dists-location = %(site_pkgs)s
    ... scripts-location = %(bin_dir)s
    ... pth-location = %(site_pkgs)s
    ... executable = %(python)s
    ... stage-locally = true
    ... """ % dict(server=link_server,
    ...	           bin_dir=os.path.join(virtenv, 'bin'),
    ...	    	   python=os.path.join(virtenv, 'bin', 'python'),
    ...     	   site_pkgs=site_pkgs))
    >>> print system(buildout), #doctest: +ELLIPSIS
    Uninstalling demo.
    Uninstalling demoneeded.
    Installing demo.
    demo: Copying demo to the staging directory.
    demo: Copying demoneeded to the staging directory.
    demo: Copying bigdemo to the staging directory.
    demo: Can't find the executable on the filesystem. Perhaps this setup is not destine to be used on this machine. So we are using the given executable value /sample-buildout/virtenv/bin/python as is.
    demo: Generated script '/sample-buildout/parts/demo-scripts/demo'.

To verify that things have been staged, let's have a closer look at the demo
script to verify everything went as planned. For one, we expect the script
to be in the parts directory::

    >>> parts_dir = os.path.join(sample_buildout, 'parts')
    >>> demo_script = os.path.join(parts_dir, 'demo-scripts', 'demo')
    >>> os.path.exists(demo_script)
    True
    >>> cat(demo_script)
    #!/sample-buildout/virtenv/bin/python
    <BLANKLINE>
    import sys
    def pth_injector(pth_file):
        path_file = open(pth_file, 'r')
        sys.path[0:0] = [line
            for line in path_file.read().split('\n')
            if line is not None]
    <BLANKLINE>
    pth_files = ['/sample-buildout/virtenv/lib/python2.6/site-packages/demo.pth']
    for pth in pth_files:
        pth_injector(pth)
    <BLANKLINE>
    import eggrecipedemo
    <BLANKLINE>
    if __name__ == '__main__':
        eggrecipedemo.main()

And also we want to check that the pth locations are correct and that the pth
itself is in the staging area with parts::

    >>> demo_pth = os.path.join(parts_dir, 'demo-pth', 'demo.pth')
    >>> cat(demo_pth)
    /sample-buildout/virtenv/lib/python2.6/site-packages/demo-0.4c1-py2.1.egg
    /sample-buildout/virtenv/lib/python2.6/site-packages/demoneeded-1.2c1-py2.1.egg
    /sample-buildout/virtenv/lib/python2.6/site-packages/bigdemo-0.1-py2.1.egg


Issues and help
===============

If you have issues or need assistance file an issue in `the bitbucket project
issue tracker <https://bitbucket.org/pumazi/buildout.recipe.isolation/issues>`_.
