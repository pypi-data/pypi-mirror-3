#!/usr/bin/env python
# Copyright (c) 2012 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import os
import re
from setuptools import setup, find_packages

VERSIONFILE = "src/frescoext/genshi/__init__.py"


def get_version():
    with open(VERSIONFILE, 'r') as f:
        return re.search(b"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read(), re.M).group(1)


def read(*path):
    """
    Read and return content from ``path``
    """
    f = open(
        os.path.join(
            os.path.dirname(__file__),
            *path
        ),
        'r'
    )
    try:
        return f.read().decode('UTF-8')
    finally:
        f.close()

setup(
    name='frescoext-genshi',
    version=get_version(),
    description='Genshi integration for fresco',
    long_description=read('README.txt') + "\n\n" + read("CHANGELOG.txt"),
    author='Oliver Cope',
    license='BSD',
    author_email='oliver@redgecko.org',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
    package_dir={'': 'src'},
    install_requires=['fresco>=0.2.1', 'Genshi>=0.6']
)
