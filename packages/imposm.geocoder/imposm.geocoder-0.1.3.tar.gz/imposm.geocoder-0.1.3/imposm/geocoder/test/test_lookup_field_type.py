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

from imposm.base import OSMElem
from imposm.geocoder.mapping import CityLookupNameGerman


def test_city_lookup_name_german_field():
    name = CityLookupNameGerman()
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg (Oldenburg)'})
    assert name.value(None, elem) == 'Oldenburg'
    assert elem.name == 'Oldenburg (Oldenburg)'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg'})
    assert name.value(None, elem) == 'Oldenburg'
    assert elem.name == 'Oldenburg'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg()'})
    assert name.value(None, elem) == 'Oldenburg'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Unterm Berg'})
    assert name.value(None, elem) == 'Unterm Berg'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Rothenburg ob der Tauber'})
    assert name.value(None, elem) == 'Rothenburg'
    
    elem = OSMElem(1, [], 'test', tags={'name': ''})
    assert name.value(None, elem) == ''
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg,Niedersachsen'})
    assert name.value(None, elem) == 'Oldenburg'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg/Niedersachsen'})
    assert name.value(None, elem) == 'Oldenburg'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg 1'})
    assert name.value(None, elem) == 'Oldenburg'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg zfdasd'})
    assert name.value(None, elem) == 'Oldenburg'
    
    elem = OSMElem(1, [], 'test', tags={'name': 'Oldenburg - Niedersachsen'})
    assert name.value(None, elem) == 'Oldenburg'