#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jsongit

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

required = ['pygit2','json_diff']
packages = ['jsongit']

setup(
    name='jsongit',
    version=jsongit.__version__,
    description='Git for JSON',
    long_description=open('README.rst').read(),
    author='John Krauss',
    author_email='john@accursedware.com',
    url='http://github.com/talos/jsongit',
    packages=packages,
    install_requires=required,
    license='BSD',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ),
)
