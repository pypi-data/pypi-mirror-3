#!/usr/bin/env python

#from distutils2.core import setup, find_packages
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import import_file

DOCUMENTATION = import_file.__doc__


setup(name='import_file',
      version='1.11',
      description='Import py files using their relative or absolute path.',
      long_description=DOCUMENTATION,
      keywords=['import', 'path', 'file'],
      author='Yuval Greenfield',
      author_email='ubershmekel@gmail.com',
      home_page='http://uberpython.wordpress.com',
      license='Public Domain',
      py_modules=['import_file'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals',
        ]
      )
