#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from distribute_setup import use_setuptools; use_setuptools()
from setuptools import setup, find_packages


rel_file = lambda *args: os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

def read_from(filename):
    fp = open(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def get_version():
    data = read_from(rel_file('src', 'djcompass', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", data).group(1)

def get_requirements():
    data = read_from(rel_file('REQUIREMENTS'))
    lines = map(lambda s: s.strip(), data.splitlines())
    return filter(None, lines)


setup(
    name             = 'django-compass2',
    version          = get_version(),
    author           = "Slawomir Ehlert",
    author_email     = "slafs.e@gmail.com",
    url              = 'http://bitbucket.org/slafs/django-compass2',
    description      = "Simple compilation of Compass projects for Django.",
    long_description = read_from('README'),
    packages         = find_packages(where='src'),
    package_dir      = {'': 'src'},
    #install_requires = get_requirements(),
)
