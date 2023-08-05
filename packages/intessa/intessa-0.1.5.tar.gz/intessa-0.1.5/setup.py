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
        'urlobject==0.6.0',
        'urecord==0.0.3',
        'requests==0.8.3',
        'odict==1.4.1',
        'simplejson==2.1.6',
        'lxml==2.3',
        'webob==1.1',
        'mock==0.7.2',
        'nose==1.1.2',
    ],
)
