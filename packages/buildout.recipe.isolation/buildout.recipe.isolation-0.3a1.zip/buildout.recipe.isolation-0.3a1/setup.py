# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
readme = os.path.join(HERE, 'buildout', 'recipe', 'isolation', 'README.rst')
readme = open(readme, 'r').read()
changes = open(os.path.join(HERE, 'CHANGES.txt'), 'r').read()

name = "buildout.recipe.isolation"
version = '0.3a1'

install_requires = [
    'setuptools',
    'zc.buildout >=1.5.2',
    ]
test_requires = [
    'zope.testing ==3.8.3',
    ]
if sys.version_info < (2, 7,):
    test_requires.append('unittest2')
extras_require = {'test': test_requires}

long_description = '\n\n'.join([readme, changes])

entry_points = """\
[zc.buildout]
default = %(package_name)s:Isolate
isolate = %(package_name)s:Isolate
pth     = %(package_name)s:PthProducer
""" % dict(package_name=name)

DEV_STATES = [
    "Development Status :: 3 - Alpha",
    "Development Status :: 4 - Beta",
    "Development Status :: 5 - Production/Stable",
]
if version.find('a') >= 0:
    state = 0
elif version.find('b') >= 0:
    state = 1
else:
    state = 2
development_status = DEV_STATES[state]

setup(
    name=name,
    version=version,
    author="Michael Mulich",
    author_email="michael.mulich@gmail.com",
    description="Recipe for isolating Python distributions " \
        "(packages and scripts).",
    long_description=long_description,
    url='https://bitbucket.org/pumazi/buildout.recipe.isolation',
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        development_status,
        ],
    keywords="development build",
    license='GPL',
    namespace_packages=['buildout', 'buildout.recipe'],
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite=name+'.tests.test_suite',
    extras_require=extras_require,
    include_package_data=True,
    zip_safe=False,
    entry_points=entry_points,
    )
