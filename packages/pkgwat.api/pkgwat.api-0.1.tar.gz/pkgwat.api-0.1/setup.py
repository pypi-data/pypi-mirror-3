#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys

f = open('README.rst')
long_description = f.read().strip()
long_description = long_description.split('split here', 1)[1]
f.close()

# Ridiculous as it may seem, we need to import multiprocessing and
# logging here in order to get tests to pass smoothly on python 2.7.
try:
    import multiprocessing
    import logging
except ImportError:
    pass

requires = [
    'six',  # For python3 support
    'requests',
]


from pkgwat.api import (
    __name__,
    __version__,
    __description__,
    __author__,
    __author_email__,
    __url__,
)


setup(
    name=__name__,
    version=__version__,
    description=__description__,
    long_description=long_description,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license='LGPLv2+',
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Topic :: System :: Archiving :: Packaging",
        "Development Status :: 4 - Beta",
    ],
    install_requires=requires,
    tests_require=[
        'nose',
        'mock',
    ],
    test_suite='nose.collector',
    packages=['pkgwat', 'pkgwat.api'],
    namespace_packages = ['pkgwat'],
    include_package_data=True,
    zip_safe=False,
)
