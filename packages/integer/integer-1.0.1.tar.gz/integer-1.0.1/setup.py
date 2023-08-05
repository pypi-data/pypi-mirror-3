#!/usr/bin/env python

##    Copyright 2012 Garrett Beaty
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

with open('README') as readme:
    description = readme.readline()
    long_description = ''.join(readme.readlines())

setup(
    name='integer',
    version='1.0.1',
    description=description,
    long_description=long_description,
    author='Garrett Beaty',
    author_email='garrett.beaty@gmail.com',
    url='https://code.google.com/p/python-integer',
    packages=['integer'],
    package_dir={'': 'src'},
    )
