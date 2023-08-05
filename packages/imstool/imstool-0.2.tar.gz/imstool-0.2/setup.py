# -*- coding: us-ascii -*-

""" ____________________________________________________________________
 
    This file is part of the imstool software package.

    Copyright (c) 2011 enPraxis, LLC
    http://enpraxis.net

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2.8  

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
    _______________________________________________________________________
"""

from setuptools import setup, find_packages
import sys, os

__author__ = 'Brent Lambert'
__copyright__ = 'Copyright 2011, enPraxis LLC'

__license__ = 'GPLv2'
__version__ = '$ Revision 0.0 $'[11:-2]
__maintainer__ = 'Brent Lambert'
__email__ = 'brent@enpraxis.net'


version = '0.2'

setup(name='imstool',
      version=version,
      description="A python library for reading and writing content packages.",
      long_description="""A python library for reading content packages from
popular open source and proprietary learning management systems. Supports IMS
Content Packaging and IMS Common Cartridge and QTI v1.2.\
""",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Software Development :: Libraries',
        ], 
      keywords='IMS, common cartridge, IMSCC, IMSCP, moodle, content package',
      author='Brent Lambert',
      author_email='brent@enpraxis.net',
      url='',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
