#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
import os.path as p

VERSION = open(p.join(p.dirname(p.abspath(__file__)), 'VERSION')).read().strip()

setup(
    name='intessa',
    version=VERSION,
    description='Zero-configuration dynamic interfaces to HTTP APIs.',
    author='Zachary Voase',
    author_email='z@zacharyvoase.com',
    url='http://github.com/zacharyvoase/intessa',
    packages=find_packages(where='lib'),
    package_dir={'': 'lib'},
    install_requires=[
        'odict>=1.4',
        'poster==0.8.1',
        'simplejson>=2',
        'urecord>=0.0.3',
        'urllib3>=1',
        'urlobject==0.6.0',
        'mock==0.8',
        'nose==1.1.2',
    ],
    extras_require={
        'xml': ['lxml==2.3'],
    },
)
