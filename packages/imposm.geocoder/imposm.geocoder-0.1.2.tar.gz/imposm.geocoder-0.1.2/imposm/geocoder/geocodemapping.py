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

from imposm.mapping import (
    Options,
    Points, LineStrings, Polygons,
    String, Bool, Integer, OneOfInt,
    set_default_name_type, LocalizedName,
    WayZOrder, ZOrder, Direction,
    GeneralizedTable, UnionView,
    PseudoArea, meter_to_mapunit, sqr_meter_to_mapunit,
)
from imposm.geocoder.mapping import (
    TrigramString,
    CityLookupNameGerman,
    GeometryLineMergeTable, GeometryUnionTable)

# # internal configuration options
# # uncomment to make changes to the default values
# import imposm.config
# 
# # import relations with missing rings
# imposm.config.import_partial_relations = False
# 
# # select relation builder: union or contains
# imposm.config.relation_builder = 'contains'
# 
# # log relation that take longer than x seconds
# imposm.config.imposm_multipolygon_report = 60
# 
# # skip relations with more rings (0 skip nothing)
# imposm.config.imposm_multipolygon_max_ring = 0
# 
# # split ways that are longer than x nodes (0 to split nothing)
# imposm_linestring_max_length = 50


# set_default_name_type(LocalizedName(['name:en', 'int_name', 'name']))

db_conf = Options(
    # db='osm',
    host='localhost',
    port=5432,
    user='osm',
    password='osm',
    sslmode='allow',
    prefix='osm_new_',
    proj='epsg:900913',
)

class Highway(LineStrings):
    fields = (
        ('tunnel', Bool()),
        ('bridge', Bool()),
        ('oneway', Direction()),
        ('ref', String()),
        ('z_order', WayZOrder()),
    )
    field_filter = (
        ('area', Bool()),
    )

places = Points(
    name = 'places',
    mapping = {
        'place': (
            'country',
            'state',
            'region',
            'county',
            'city',
            'town',
            'village',
            'hamlet',
            'suburb',
            'locality',
        ),
    },
    fields = (
        ('z_order', ZOrder([
            'country',
            'state',
            'region',
            'county',
            'city',
            'town',
            'village',
            'hamlet',
            'suburb',
            'locality',
        ])),
        ('population', Integer()),
        ('lookup_name', CityLookupNameGerman()),
        ('name', TrigramString()),
    ),
)

admin = Polygons(
    name = 'admin',
    mapping = {
        'boundary': (
            'administrative',
        ),
    },
    fields = (
        ('admin_level', OneOfInt('1 2 3 4 5 6 7 8 9 10'.split())),
        ('name', TrigramString()),
    ),
)

motorways = Highway(
    name = 'motorways',
    fields = Highway.fields + (
        ('name', TrigramString()),
    ),
    mapping = {
        'highway': (
            'motorway',
            'motorway_link',
            'trunk',
            'trunk_link',
        ),
    }
)

mainroads = Highway(
    name = 'mainroads',
    fields = Highway.fields + (
        ('name', TrigramString()),
    ),
    mapping = {
        'highway': (
            'primary',
            'primary_link',
            'secondary',
            'secondary_link',
            'tertiary',
    )}
)

minorroads = Highway(
    name = 'minorroads',
    fields = Highway.fields + (
        ('name', TrigramString()),
    ),
    mapping = {
        'highway': (
            'road',
            'path',
            'track',
            'service',
            'footway',
            'bridleway',
            'cycleway',
            'steps',
            'pedestrian',
            'living_street',
            'unclassified',
            'residential',
    )}
)


roads = UnionView(
    name = 'roads',
    fields = (
        ('bridge', 0),
        ('ref', None),
        ('tunnel', 0),
        ('oneway', 0),
        ('z_order', 0),
    ),
    mappings = [mainroads, minorroads],
)

# TODO new view for minor and mainroads, exclude cycleways?!

#TODO index addr:postcode also?
point_addresses = Points(
    name = 'point_addresses',
    with_type_field = False,
    fields = (
        ('addr:street', TrigramString()),
        ('addr:postcode', String()),
        ('addr:city', TrigramString()),
        ('addr:country', TrigramString()),
        ('addr:housenumber', TrigramString()),
    ),
    mapping = {
        'addr:housenumber': (
            '__any__',
        ),
    }
)

polygon_addresses = Polygons(
    name = 'polygon_addresses',
    with_type_field = False,
    fields = (
        ('addr:street', TrigramString()),
        ('addr:postcode', String()),
        ('addr:city', TrigramString()),
        ('addr:country', TrigramString()),
        ('addr:housenumber', TrigramString()),
    ),
    mapping = {
        'addr:housenumber': (
            '__any__',
        ),
    }
)

addresses = UnionView(
    name = 'addresses',
    fields = (
        ('addr:street', String()),
        ('addr:postcode', String()),
        ('addr:city', String()),
        ('addr:country', String()),
        ('addr:housenumber', String()),
    ),
    mappings = [point_addresses, polygon_addresses],
)

postcodes = Polygons(
    name= 'postcode',
    with_type_field = False,
    fields = (
        ('postal_code', String()),
    ),
    mapping = {
        'postal_code': (
            '__any__',
        ),
    }
)

postcodes_unified = GeometryUnionTable(
    name = 'postcodes_union',
    origin = postcodes,
    group_by = 'postal_code',
)

roads_merged = GeometryLineMergeTable(
    name = 'roads_merged',
    origin = roads,
    group_by = 'name',
)