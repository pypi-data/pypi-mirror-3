import os
import sys
from setuptools import setup, find_packages

install_requires=['SQLAlchemy',
                    'GeoAlchemy',
                    'psycopg2',
                    'imposm'
                    ]

if sys.version_info < (2, 7):
    install_requires.append('argparse')

readme = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(name='imposm.geocoder',
      version='0.1.1',
      description='Imposm Geocoder for OSM-Data',
      long_description=readme,
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
)