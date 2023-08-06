#!/usr/bin/env python
# Closure Depresolver
# Copyright (C) 2012  Paul Horn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='closure_depresolver',
    version='0.0.1',
    description='Scans your CL files to help you correctly goog.providing and goog.requiring your classes.',
    license='GPLv3',
    author='Paul Horn',
    author_email='knutwalker@gmail.com',
    url='https://github.com/knutwalker/closure_depresolver',

    install_requires=['argparse'],

    package_dir={'closure_depresolver': 'closure_depresolver'},
    packages=['closure_depresolver'],

    entry_points = {
      'console_scripts': [
        'gjsresolve = closure_depresolver.clresolve:main'
      ]
    }
)