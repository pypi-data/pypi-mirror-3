#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

version_tuple = __import__('pyschroot').VERSION
version = '.'.join([str(v) for v in version_tuple])

setup(
    name = 'pyschroot',
    version = version,
    description = 'Python wrapper for the Linux schroot command',
    author = 'Bernhard Janetzki',
    author_email = 'boerni@gmail.com',
    url = 'https://bitbucket.org/boerni/pyschroot',
    packages = ['pyschroot'],
)