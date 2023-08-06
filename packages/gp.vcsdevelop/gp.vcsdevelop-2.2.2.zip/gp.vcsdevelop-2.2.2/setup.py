# -*- coding: utf-8 -*-
# Copyright (C)2009 'Gael Pasgrimaud'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module contains the tool of gp.vcsdevelop
"""
import os
from setuptools import setup, find_packages

version = '2.2.2'

README = os.path.join('README.txt')
RECIPE = os.path.join('docs', 'recipe.txt')
CHANGES = os.path.join('docs', 'news.txt')

long_description = """
%s

%s

Changes
=======

%s

Download
========

""" % (open(README).read(), open(RECIPE).read(), open(CHANGES).read())

tests_require = [
        'zope.event',
        'zope.interface',
        'zope.testing',
        'zc.buildout',
        'zc.recipe.egg',
        'ConfigObject',
    ]

setup(name='gp.vcsdevelop',
      version=version,
      description="ZC buildout extension to checkout eggs from various vcs",
      long_description=long_description,
      classifiers=[
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        ],
      keywords='buildout extension vcs develop',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org/docs/gp.vcsdevelop/index.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'bootstrap',
                                      'bootstrap-py3k', 'pip']),
      namespace_packages=['gp'],
      include_package_data=True,
      zip_safe=False,
      test_suite="gp.vcsdevelop.tests.test_suite",
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      install_requires=[
          'setuptools',
          'zc.buildout',
      ],
      entry_points = """
      [zc.buildout.extension]
      default = gp.vcsdevelop:install
      """
      )

