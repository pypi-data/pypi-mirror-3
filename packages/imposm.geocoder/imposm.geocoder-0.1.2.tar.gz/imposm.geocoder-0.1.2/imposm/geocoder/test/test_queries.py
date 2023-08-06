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
import re
import os
import tempfile
import shutil

from contextlib import contextmanager

from imposm.geocoder.config import load_config
from imposm.geocoder.model import init_model, geocode

from nose.tools import eq_
from nose.plugins import skip


def setup_module():
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/geocoder.ini')
    init_model(load_config(config_file))

class TestQueryBase(object):
    def __init__(self):
        self.params = {
            'road': None,
            'city': None,
            'housenumber': None,
            'postcode': None,
            'country': None,
        }        

class TestQueryTypes(TestQueryBase):
    def test_osm_query_road(self):
        self.params['road'] = u'Musterstra\xc3e'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryRoad')
        
    def test_osm_query_place(self):
        self.params['city'] = 'Stadt am Fluss'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryPlace')
        
    def test_osm_query_country(self):
        self.params['country'] = 'Deutschland'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryCountry')
        
    def test_osm_query_postcode(self):
        self.params['postcode'] = '99999'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryPostcode')
        
    def test_osm_query_address(self):
        self.params['housenumber'] = '1'
        self.params['city'] = 'Stadt am Fluss'
        self.params['road'] = 'X-Weg'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryAddress')
        
    def test_osm_query_address_place_road(self):
        self.params['city'] = 'Stadt am Fluss'
        self.params['road'] = 'X-Weg'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryAddressPlaceRoad')
        
    def test_osm_query_admin_place_road(self):
        self.params['city'] = 'Dorf B'
        self.params['road'] = u'Musterstra\xc3e'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryAdminPlaceRoad')
        
    def test_osm_query_postcode_place_road(self):
        self.params['city'] = 'Stadt am Fluss'
        self.params['postcode'] = '01234'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryPostcodePlaceRoad')
        
        self.params['road'] = 'X-Weg'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryPostcodePlaceRoad')
        
        self.params['city'] = None
        self.params['road'] = 'X-Weg'
        self.params['postcode'] = '01234'
        results = geocode(self.params)
        eq_(results[0]['properties']['query_type'], 'OSMQueryPostcodePlaceRoad')
        
class TestQueryResults(TestQueryBase):
    def test_roads(self):
        self.params['road'] = 'X-Weg'
        results = geocode(self.params)
        # due to fuzzy string match, 2 results are returned
        eq_(len(results), 2)
        eq_(results[0]['properties']['road']['name'], 'X-Weg')
        eq_(results[0]['properties']['address']['city'], 'Stadt am Fluss')
        
        eq_(results[1]['properties']['road']['name'], 'T-Weg')
        eq_(results[1]['properties']['city']['name'], 'Stadt am Fluss')
        
        self.params['road'] = 'Unbekannt'
        results = geocode(self.params)
        eq_(len(results), 0)
        
    def test_places(self):
        self.params['city'] = 'Stadt am Fluss'
        results = geocode(self.params)
        eq_(len(results), 1)
        eq_(results[0]['properties']['city']['name'], 'Stadt am Fluss')
        
        self.params['city'] = 'Dorf A'
        results = geocode(self.params)
        eq_(len(results), 2)
        eq_(results[0]['properties']['city']['name'], 'Dorf A')
        eq_(results[1]['properties']['city']['name'], 'Dorf B')
        
        self.params['city'] = 'Zufalls'
        results = geocode(self.params)
        eq_(len(results), 1)
        eq_(results[0]['properties']['city']['name'], 'Zufallsstadt')
        
        self.params['city'] = 'Unbekannt'
        results = geocode(self.params)
        eq_(len(results), 0)
        
    def test_postcodes(self):
        self.params['postcode'] = '99999'
        results = geocode(self.params)
        eq_(len(results), 1)
        eq_(results[0]['properties']['postcode']['postcode'], '99999')
        
        self.params['postcode'] = '20202'
        results = geocode(self.params)
        eq_(len(results), 0)
        
    def test_countries(self):
        self.params['country'] = 'Deutschland'
        results = geocode(self.params)
        eq_(len(results), 1)
        eq_(results[0]['properties']['country']['name'], 'Deutschland')
        eq_(results[0]['properties']['country']['admin_level'], 2)
        
    def test_addresses(self):
        self.params['housenumber'] = '2'
        self.params['road'] = 'X-Weg'
        self.params['city'] = 'Stadt am Fluss'
        results = geocode(self.params)
        eq_(len(results), 1)
        eq_(results[0]['properties']['address']['city'], 'Stadt am Fluss')
        eq_(results[0]['properties']['address']['housenumber'], '2')
        eq_(results[0]['properties']['address']['street'], 'X-Weg')
        eq_(results[0]['properties']['address']['postcode'], '01234')
        eq_(results[0]['properties']['address']['country'], 'DE')