#!/usr/bin/env python
# coding: utf-8

# Copyright 2011 - Mickaël THOMAS

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(name='gett-cli',
      version='0.2.2',
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

