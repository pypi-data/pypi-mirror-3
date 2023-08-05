#!/usr/bin/env python

from distutils.core import setup

setup(name='DARE',
      version='0.7',
      description='Dynamic Application Runtime Environment',
      author='Sharath Maddineni',
      author_email='smaddinenid@cct.lsu.edu',
      url='http://dare.cct.lsu.edu/',
      packages=['dare'],
      data_files=['dare.conf'],
      #install_requires=['bigjob', 'troy'],
     )
