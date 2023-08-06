#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


required = ["poster"]


setup(
    name='iron-worker',
    version='0.0.1',
    description='The Python client for IronWorker, a cloud service for background processing.',
    author='Iron.io',
    url='http://iron.io/products/worker',
    install_requires=required,
    packages=[ 'iron_worker' ],
)
