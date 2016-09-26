#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

packages = ['quantitative',
            'quantitative.core',
            'quantitative.example']

setup(name='quantitative',
      version='1.0b',
      description='Quantitative finance,and back testing library',
      url='https://github.com/jeffrey-liang/quantitative',
      author='Jeffrey Liang',
      author_email='jeffrey_liang@sfu.ca',
      license='Apache 2.0',

      classifers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Financial and Insurance Industry',
          'Intended Audience :: Science/Research',
          'Topic :: Office/Business :: Financial',
          'Topic :: Office/Business :: Financial :: Investment',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.5'
      ],
      keywords='quantitative backtesting finance quant finance stocks',
      install_requires=['pandas', 'numpy', 'scipy'],
      packages=find_packages(exclude=['dev_files']),
      zip_safe=False)
