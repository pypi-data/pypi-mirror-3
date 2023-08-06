# This file is part of imposm.geocoder.
# Copyright 2012 Omniscale (http://omniscale.com)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
from setuptools import setup, find_packages

install_requires=['SQLAlchemy',
                    'GeoAlchemy',
                    'psycopg2',
                    'imposm>=2.3.3'
                    ]

if sys.version_info < (2, 7):
    install_requires.append('argparse')

readme = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(name='imposm.geocoder',
      version='0.1.3',
      url='http://geocoder.imposm.org',
      description='Imposm Geocoder for OSM-Data',
      long_description=readme,
      license='Apache Software License 2.0',
      author='Marcel Radischat',
      author_email='radischat@omniscale.de',
      packages=find_packages(),
      install_requires=install_requires,
      include_package_data=True,
      package_data = {'': ['*.ini', '*.sql']},
      namespace_packages = ['imposm'],
      entry_points = {
          'console_scripts': [
              'imposm-geocoder = imposm.geocoder.app:main',
          ],
      },
      classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)