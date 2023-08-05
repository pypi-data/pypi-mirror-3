# -*- coding: utf-8 -*-
# Copyright (C) 2011 Alterway Solutions 

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

from setuptools import setup, find_packages
import os

version = '0.10'
install_requires = []
if os.name == 'nt':
    install_requires = ['WMI',]
long_description = open(os.path.join("docs","source","index.rst")).read()
long_description = long_description[:long_description.index('Contents:')]

setup(name='aws.windowsplonecluster',
      version=version,
      description="A super script to control a zope/apache/pound/squid cluster for windows",
      long_description= long_description +
                        "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='windows service pound zope',
      author='Youenn Boussard',
      author_email='youenn.boussard@alterway.fr',
      url='https://github.com/yboussard/aws.windowsplonecluster',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['aws'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-'
          'zope.interface',
          'zope.component',
          
      ] + install_requires, 
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ctl = aws.windowsplonecluster:main
      """,
      )
