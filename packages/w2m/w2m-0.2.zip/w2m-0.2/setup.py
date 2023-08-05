#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

####
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ... Taken from
# http://packages.python.org/an_example_pypi_project/setuptools.html
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

####

setup(name='w2m',
      version='0.2',
      py_modules=['w2m'],
      description='www spider producing an adjacency matrix',
      long_description=read('README'),
      keywords='www, social networks, random oriented graphs, adjacency matrix, spectrum, eigenvalues, edges, vertices',
      platforms='All',
      author='Djalil CHAFAI',
      author_email='djalil@chafai.net',
      url='http://djalil.chafai.net/',
      license='GNU General Public License (GPL)',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Visualization'
          ]
      )
