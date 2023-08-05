#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(name='gett-cli',
      version='0.2.1',
      description='A command-line Ge.tt uploader and manager',
      author='Mickaël THOMAS',
      author_email='mickael9@gmail.com',
      url='https://bitbucket.org/mickael9/gett-cli/',
      py_modules=['gett', 'gett_uploader'],
      install_requires=['distribute'],
      entry_points = {
          'console_scripts': [
              'gett = gett_uploader:entry_point'
          ]
      }
     )

