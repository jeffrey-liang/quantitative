#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='quantitative',
    version='1.0.0',
    description='Event-Driven Backtest Library',
    author='Jeffrey Liang',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pandas', 'numpy']
)
