# -:- encoding: UTF8 -:-
# Copyright 2011 Omniscale (http://omniscale.com)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from imposm.mapping import String
from imposm.db.postgis import TrigramIndex

class TrigramString(String, TrigramIndex):
   pass

class GroupByTable(object):
    def __init__(self, name, origin, group_by=None):
        self.name = name
        self.origin = origin
        self.group_by = group_by

class GeometryUnionTable(GroupByTable):
    pass
        
class GeometryLineMergeTable(GroupByTable):
    pass

class CityLookupNameGerman(String, TrigramIndex):
    """
    Field for lookup names.
    Converts a name of a place to an shorter one for geocoding purposes.
    
    :PostgreSQL datatype: VARCHAR(255)
    """
    def extra_fields(self):
        return []
        
    def value(self, val, osm_elem):
        val = osm_elem.tags.get('name')
        
        if val is None:
            return val
        
        has_prefixes = re.compile('^(An|Am|In|Im|Vor|Vorm|Hinter|Hinterm|Unter|Über|Rechts|Links|Auf) ')

        if has_prefixes.search(val):
            return val
        #\xc3\xa4 ae
        #\xc3\xb6 oe
        #\xc3\xbc ue
        #\xc3\x9f sz
        suffixes = re.compile('( [a-z\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f0-9\\(\\)\\\\/-]+ ?)+|/|,|\\(')
        match = suffixes.search(val)

        if match is not None:
            val = val[:match.start()]

        return val
