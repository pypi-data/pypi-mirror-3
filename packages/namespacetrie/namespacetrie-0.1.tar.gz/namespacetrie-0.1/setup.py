#!/usr/bin/env python
# Namespace Trie
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

__author__ = 'knutwalker@gmail.com (Paul Horn)'


import os.path

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    find_packages = lambda : ['namespacetrie', 'tests']

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fh:
        return fh.read()

setup(
    name='namespacetrie',
    version='0.1',
    description=('A Trie implementation that manages not the single characters'
                 ' but treats its values as typical namespaces.'),
    license='GPLv3',
    author='Paul Horn',
    author_email='knutwalker@gmail.com',
    url='https://github.com/knutwalker/namespacetrie',

    keywords = "namespace trie",
    long_description=read('README'),

    install_requires=['weakrefset', 'ordereddict'],

    package_dir={'namespacetrie': 'namespacetrie'},
    packages=find_packages(),

    test_suite="tests"
)
