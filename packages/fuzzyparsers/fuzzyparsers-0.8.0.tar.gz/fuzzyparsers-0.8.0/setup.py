#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2010-12, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of The MIT License
##############################################################################

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='fuzzyparsers',
    version='0.8.0',  # also update in fuzzyparsers/__init__.py
    description='A collection of free-form input parsers (with special focus on dates)',
    license='MIT',
    author='Joel B. Mohler',
    author_email='joel@kiwistrawberry.us',
    long_description=read('README.txt'),
    url='https://bitbucket.org/jbmohler/fuzzyparsers',
    packages=['fuzzyparsers'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent"])
