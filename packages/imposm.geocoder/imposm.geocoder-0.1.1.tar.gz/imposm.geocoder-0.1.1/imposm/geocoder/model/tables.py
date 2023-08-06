"""SQLAlchemy ORM"""

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper
from geoalchemy import GeometryExtensionColumn, GeometryColumn, Point, LineString, Polygon, MultiLineString, Geometry
from geoalchemy.postgis import PGComparator
from imposm.geocoder.model import meta

class Address(object):
    def __init__(self, osm_id, name, housenumber, country, postcode, city, street, geometry):
        self.osm_id = osm_id
        self.name = name
        self.housenumber = housenumber
        self.country = country
        self.postcode = postcode
        self.city = city
        self.street = street
        self.geometry = geometry
        
class LookupPlace(object):
    def __init__(self, osm_id, lookup_name, name, type, z_order, population, geometry):
        self.osm_id = osm_id
        self.name = name
        self.type = type
        self.lookup_name = lookup_name
        self.z_order = z_order
        self.population = population
        self.geometry = geometry
    
class Admin(object):
    def __init__(self, osm_id, name, type, admin_level, geometry):
        self.osm_id = osm_id
        self.name = name
        self.type = type
        self.admin_level = admin_level
        self.geometry = geometry
    
class Postcode(object):
    def __init__(self, id, postcode, geometry):
        self.id = id
        self.postcode = postcode
        self.geometry = geometry
    
class UnifiedRoad(object):
    def __init__(self, id, name, osm_ids, geometry):
        self.id = id
        self.name = name
        self.osm_ids = osm_ids
        self.geometry = geometry
    
def map_config(config):
    address = Table('%s' % (config.tablenames['addresses']),
                    meta.metadata,
                    Column('osm_id', Integer, primary_key=True),
                    Column('name', String()),
                    Column('addr:housenumber', String()),
                    Column('addr:country', String()),
                    Column('addr:postcode', String()),
                    Column('addr:city', String()),
                    Column('addr:street', String()),
                    GeometryExtensionColumn('geometry', Point(2, srid=config.srid))
                    )
    place = Table('%s' % (config.tablenames['places']),
                    meta.metadata,
                    Column('osm_id', Integer, primary_key=True),
                    Column('lookup_name', String()),
                    Column('name', String()),
                    Column('type', String()),
                    Column('z_order', Integer()),
                    Column('population', Integer()),
                    GeometryExtensionColumn('geometry', Point(2, srid=config.srid))
                    )
    admin = Table('%s' % (config.tablenames['admin']),
                    meta.metadata,
                    Column('osm_id', Integer, primary_key=True),
                    Column('name', String()),
                    Column('type', String()),
                    Column('admin_level', Integer()),
                    GeometryExtensionColumn('geometry', Polygon(2, srid=config.srid))
                    )
    postcode = Table('%s' % (config.tablenames['postcodes']),
                    meta.metadata,
                    Column('id', Integer, primary_key=True),
                    Column('postcode', String()),
                    GeometryExtensionColumn('geometry', Polygon(2, srid=config.srid))
                    )
    road = Table('%s' % (config.tablenames['roads']),
                    meta.metadata,
                    Column('id', Integer, primary_key=True),
                    Column('name', String()),
                    Column('osm_ids', Integer()),
                    GeometryExtensionColumn('geometry', MultiLineString(2, srid=config.srid))
                    )
    mapper(Address, address, properties={
                                'geometry': GeometryColumn(address.c.geometry, comparator=PGComparator),
                                'street': address.c.get('addr:street'),
                                'country': address.c.get('addr:country'),
                                'postcode': address.c.get('addr:postcode'),
                                'city': address.c.get('addr:city'),
                                'housenumber': address.c.get('addr:housenumber'),
                                'name': address.c.name,
                                'osm_id': address.c.osm_id})
    mapper(LookupPlace, place, properties={
                                'geometry': GeometryColumn(place.c.geometry, comparator=PGComparator),
                                'lookup_name': place.c.lookup_name,
                                'name': place.c.name,
                                'osm_id': place.c.osm_id,
                                'z_order': place.c.z_order,
                                'population': place.c.population,
                                'type': place.c.type})
    mapper(Admin, admin, properties={
                                'geometry': GeometryColumn(admin.c.geometry, comparator=PGComparator),
                                'name': admin.c.name,
                                'type': admin.c.type,
                                'osm_id': admin.c.osm_id,
                                'admin_level': admin.c.admin_level})
    mapper(Postcode, postcode, properties={
                                'geometry': GeometryColumn(postcode.c.geometry, comparator=PGComparator),
                                'postcode': postcode.c.postcode,
                                'id': postcode.c.id})
    mapper(UnifiedRoad, road, properties={
                                'geometry': GeometryColumn(road.c.geometry, comparator=PGComparator),
                                'name': road.c.name,
                                'id': road.c.id,
                                'osm_ids': road.c.osm_ids})