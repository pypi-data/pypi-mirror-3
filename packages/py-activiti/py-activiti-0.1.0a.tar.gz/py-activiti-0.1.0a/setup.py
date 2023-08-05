#    Coding: utf-8

#    py-activiti - Python Wrapper For Activiti BPMN2.0 API
#    Copyright (C) 2011  xtensive.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

from setuptools import setup, find_packages
import sys, os

version = '0.1.0a'

setup(name='py-activiti',
      version=version,
      description="Activiti BPMN2.0 API Wrapper",
      long_description="""Python library which wraps Activiti BPMN2.0 Engine API""",
      classifiers=['Development Status :: 2 - Pre-Alpha', 
                   'Environment :: Other Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Libraries :: Python Modules'], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Activiti API BPM 2.0',
      author='Thierry MICHEL',
      author_email='thierry@xtensive.com',
      url='https://sourceforge.net/p/pyactiviti/home/Home/',
      license='GPLv3',
      package_dir= {'': 'src'},
      packages=['activiti'],
      include_package_data=True,
      #zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
