import re
from itertools import izip
from sqlalchemy.sql.expression import desc
from sqlalchemy.orm import aliased
from sqlalchemy import create_engine, func
from geoalchemy.functions import functions
from geoalchemy.base import DBSpatialElement

from imposm.geocoder.model import meta
from imposm.geocoder.model.tables import Address, Admin, Postcode, UnifiedRoad, LookupPlace, map_config

def init_model(config):
    """
    initialise db-engine and bind metadata
    """
    engine = create_engine(config.database, echo=False)
    meta.engine = engine
    meta.Session.configure(bind=engine)
    meta.metadata.bind = engine
    #set limit for trigrams
    meta.engine.execute(func.set_limit(0.47))
    map_config(config)
    #meta.metadata.create_all(checkfirst=)
    
def meter_to_sridunit(srid, meter):
    if srid == '4326':
        deg_to_meter = (40000 * 1000) / 360
        return meter / deg_to_meter
    if srid == '900913':
        return meter
    return meter

class DictWrapper(object):
    """
    this class wraps the results of the geocoding process,
    additional informations will be added and calculated
    """
    def __init__(self, query_type, addresses=None, roads=None, places=None, postcodes=None, countries=None):
        self._session = None
        self.query_type = query_type
        self.addresses = addresses
        self.roads = roads
        self.places = places
        self.postcodes = postcodes
        self.countries = countries
        self.results = []
    
    @property
    def session(self):
        if self._session is None:
            self._session = meta.Session()
        return self._session
    
    def has_results(self):
        """if anything is set, proceed"""
        return any([self.roads, self.places, self.addresses, self.postcodes, self.countries])
    
    def add_base_dict(self):
        """results will be added"""
        #TODO add real bbox and one for display?
        new_dict = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': None,
            },
            'properties': {
                'display_name': None,
                'query_type': self.query_type,
            },
            'bbox': None,
        }
        self.results.append(new_dict)
    
    def add_admin_levels(self, index, osm_element):
        """calculate admin leves for each osm_element"""
        q = self.session.query(Admin)
        q = q.filter(functions.intersects(Admin.geometry, osm_element.geometry))
        q = q.order_by(Admin.admin_level)
        
        admin_levels = []
        for admin in q:
            admin_levels.append({admin.admin_level: admin.name})
        
        self.results[index]['properties']['admin_levels'] = admin_levels
    
    def calculate_additional_data(self):
        if self.addresses and self.roads is None:
            #add addresses to result-list
            for index, address in enumerate(self.addresses):
                self.add_base_dict()
                display_name = '%s %s, %s' % (address.street, address.housenumber, address.city)
                self.add_metadata(index, address, display_name=display_name, with_buffer=True)
                self.add_address(index, address)
                
        if self.roads and self.postcodes is None:
            #get the place to which each road belongs
            if self.addresses:
                for index, (road, address) in enumerate(izip(self.roads, self.addresses)):
                    self.add_base_dict()
                    display_name = '%s, %s' % (road.name, address.city)
                    self.add_metadata(index, road, display_name=display_name, snapped=True)
                    self.add_road(index, road)
                    self.add_address(index, address)
                    self.add_admin_levels(index, road)
            else:
                #search for addresses within 100m of the road
                for index, road in enumerate(self.roads):
                    self.add_base_dict()
                    buf = functions.buffer(road.geometry, meter_to_sridunit(road.geometry.srid, 100))
                    q = self.session.query(Address)
                    q = q.filter(functions.intersects(Address.geometry, buf))
                    q = q.filter(Address.street == road.name)
                    q = q.limit(1)

                    if q.count() > 0:
                        address = q.one()
                        #add the right place, if an address is found
                        if address.city is not None:
                            display_name = '%s, %s' % (address.city, road.name)
                            self.add_metadata(index, road, display_name=display_name, snapped=True)
                            self.add_road(index, road)
                            self.add_address(index, address)
                            self.add_admin_levels(index, road)

                #look for places near the road with admin_level=8 (city or commune/municipal in germany)
                for index, road in enumerate(self.roads):
                    if self.results[index]['properties']['display_name'] is None:
                        q = self.session.query(LookupPlace)
                        q = q.join(Admin, functions.intersects(Admin.geometry, LookupPlace.geometry))
                        q = q.filter(Admin.admin_level == 8)
                        #geometries shall intersect
                        q = q.filter(functions.intersects(Admin.geometry, road.geometry))
                        #only places with type city, town, village, hamlet
                        q = q.filter(LookupPlace.type.in_(['city', 'town', 'village', 'hamlet']))
                        q = q.filter(LookupPlace.name != None)
                        #order results by distance
                        q = q.order_by(functions.distance(LookupPlace.geometry, road.geometry))
                        q = q.limit(1)

                        if q.count() > 0:
                            place = q.one()
                            display_name = '%s, %s' % (place.name, road.name)
                            self.add_metadata(index, road, display_name=display_name, snapped=True)
                            self.add_road(index, road)
                            self.add_place(index, place)
                            self.add_admin_levels(index, road)
                            
                #look for places near the road with distance-check
                for index, road in enumerate(self.roads):
                    #if no place was found yet, get the nearest place
                    if self.results[index]['properties']['display_name'] is None:
                        dist = functions.distance(LookupPlace.geometry, road.geometry)
                        #every place within 20000m 
                        q = self.session.query(LookupPlace).filter(dist < meter_to_sridunit(LookupPlace.geometry.srid, 20000))
                        q = q.filter(LookupPlace.type.in_(['city', 'town', 'village', 'village', 'hamlet']))
                        #name has to be set
                        q = q.filter(LookupPlace.name != None)
                        #order by distance
                        q = q.order_by(dist)
                        q = q.limit(1)

                        place = q.one()
                        display_name = '%s, %s' % (place.name, road.name)
                        self.add_metadata(index, road, display_name=display_name, snapped=True)
                        self.add_road(index, road)
                        self.add_place(index, place)
                        self.add_admin_levels(index, road)
        
        if self.places and self.postcodes is None:
            #add ever place to the final results
            for index, place in enumerate(self.places):
                self.add_base_dict()
                self.add_admin_levels(index, place)
                admin_levels = self.results[index]['properties']['admin_levels']
                try:
                    level6 = (tmp_dict[6] for tmp_dict in admin_levels if tmp_dict.get(6, False)).next()
                except StopIteration:
                    level6 = admin_levels
                display_name = '%s, %s' % (place.name, level6)
                self.add_metadata(index, place, display_name=display_name, with_buffer=True)
                self.add_place(index, place)
                
        if self.postcodes:
            #add ever postcode to the final results and check if roads and places shall also be added
            if self.roads and self.places:
                for index, (road, postcode) in enumerate(izip(self.roads, self.postcodes)):
                    #get the correct place
                    dist = functions.distance(LookupPlace.geometry, road.geometry)
                    q = self.session.query(LookupPlace)
                    q = q.filter( dist < meter_to_sridunit(LookupPlace.geometry.srid, 20000))
                    q = q.order_by(dist)
                    q = q.limit(1)
                    place = q.one()
                    
                    self.add_base_dict()
                    display_name = '%s, %s %s' % (road.name, postcode.postcode, place.name)
                    self.add_metadata(index, road, display_name=display_name, snapped=True)
                    self.add_road(index, road)
                    self.add_place(index, place)
                    self.add_postcode(index, postcode)
                    self.add_admin_levels(index, road)
            elif self.places:
                for index, (place, postcode) in enumerate(izip(self.places, self.postcodes)):
                    self.add_base_dict()
                    display_name = '%s %s' % (postcode.postcode, place.name)
                    #TODO display postcode or place as centroid?
                    self.add_metadata(index, postcode, display_name=display_name)
                    self.add_place(index, place)
                    self.add_postcode(index, postcode)
                    self.add_admin_levels(index, postcode)
            elif self.roads:
                for index, (road, postcode) in enumerate(izip(self.roads, self.postcodes)):
                    self.add_base_dict()
                    display_name = '%s, %s' % (road.name, postcode.postcode)
                    self.add_metadata(index, road, display_name=display_name, snapped=True)
                    self.add_road(index, road)
                    self.add_postcode(index, postcode)
                    self.add_admin_levels(index, road)
            else:
                for index, postcode in enumerate(self.postcodes):
                    self.add_base_dict()
                    q = self.session.query(Address.city)
                    q = q.filter(functions.intersects(Address.geometry, postcode.geometry))
                    q = q.filter(Address.city != None)
                    q = q.group_by(Address.city)

                    where = ', '.join([address.city for address in q])
                
                    self.add_metadata(index, postcode, display_name=postcode.postcode)
                    self.add_postcode(index, postcode)
                    self.add_admin_levels(index, postcode)
                    if where != '':
                        self.results[index]['properties']['places_with_postcode'] = where
                    
        if self.countries:
            for index, country in enumerate(self.countries):
                self.add_base_dict()
                self.add_metadata(index, country, display_name=country.name)
                self.add_country(index, country)
    
    def add_metadata(self, index, osm_element, display_name=None, with_buffer=False,  snapped=False):
        """add metadata"""
        if with_buffer:
            #only places and addresses
            if getattr(osm_element, 'type', False):
                if osm_element.type == 'city':
                    radius = meter_to_sridunit(osm_element.geometry.srid, 5000)
                elif osm_element.type == 'town':
                    radius = meter_to_sridunit(osm_element.geometry.srid, 2500)
                elif osm_element.type == 'suburb' or osm_element.type == 'village':
                    radius = meter_to_sridunit(osm_element.geometry.srid, 1000)
                elif osm_element.type == 'hamlet':
                    radius = meter_to_sridunit(osm_element.geometry.srid, 500)
                else:
                    radius = meter_to_sridunit(osm_element.geometry.srid, 100)
            else:
                radius = meter_to_sridunit(osm_element.geometry.srid, 100)
            buf = functions.buffer(osm_element.geometry, radius)
            bbox = DBSpatialElement(self.session.scalar(functions.envelope(buf)))
        else:
            bbox = DBSpatialElement(self.session.scalar(osm_element.geometry.envelope()))
            
        if snapped:
            #snap the centroid to the road
            centroid = DBSpatialElement(self.session.scalar(func.multiline_center(osm_element.geometry.wkb,    osm_element.geometry.centroid().wkb)))
        else:
            centroid = DBSpatialElement(self.session.scalar(osm_element.geometry.centroid()))
        
        #add a bounding box
        _bbox = []
        if self.session.scalar(bbox.geometry_type) == 'ST_Polygon':
            for coord_pair in bbox.coords(self.session)[0][:4:2]:
                _bbox.append(coord_pair[0])
                _bbox.append(coord_pair[1])
        else:
            _bbox = centroid.coords(self.session)*2
        self.results[index]['geometry']['coordinates'] = centroid.coords(self.session)
        self.results[index]['properties']['display_name'] = display_name
        self.results[index]['bbox'] = _bbox
    
    def add_address(self, index, address):
        self.results[index]['properties']['address'] = {
            'name': address.name,
            'id': address.osm_id,
            'housenumber': address.housenumber,
            'street': address.street,
            'city': address.city,
            'postcode': address.postcode,
            'country': address.country,
        }
    
    def add_road(self, index, road):
        self.results[index]['properties']['road'] = {
            'name': road.name,
            'id': road.id,
            'osm_ids': ', '.join(map(str,road.osm_ids)),
            'type': 'merged_road',
        }
    
    def add_place(self, index, place):
        self.results[index]['properties']['city'] = {
            'name': place.name,
            'lookup_name': place.lookup_name,
            'id': place.osm_id,
            'type': place.type,
        }
     
    def add_postcode(self, index, postcode):
        self.results[index]['properties']['postcode'] = {
            'id': postcode.id,
            'postcode': postcode.postcode,
        }
    
    def add_country(self, index, country):
        self.results[index]['properties']['country'] = {
            'name': country.name,
            'id': country.osm_id,
            'type': country.type,
            'admin_level': country.admin_level,
        }
        
    def get_results(self):
        return self.results
    
class OSMQueryBase(object):
    """base class"""
    def __init__(self, params):
        self.params = params
        self._query = None
        self._session = None
        self._with_suffixes = False
    
    @property
    def query(self):
        if self._query is None:
            self._query = self._build_query()
        return self._query
        
    @property
    def session(self):
        if self._session is None:
            self._session = meta.Session()
        return self._session
    
    def is_valid(self):
        raise NotImplementedError
    
    def _build_query(self):
        raise NotImplementedError
    
    def result(self, limit=None, offset=None):
        raise NotImplementedError
    
class OSMQueryRoad(OSMQueryBase):
    """query roads"""
    def is_valid(self):
        if self.params['road'] is None:
            return False
        return True
    
    def _build_query(self):
        #similarity roadname
        similarity = func.similarity(UnifiedRoad.name, self.params['road'])
        #query roads
        query = self.session.query(UnifiedRoad)
        #filter data
        query = query.filter(UnifiedRoad.name % self.params['road'])
        #check if search shall be limited by a country
        if self.params['country'] is not None:
            query = query.join(Admin, functions.intersects(Admin.geometry, UnifiedRoad.geometry))
            #admin_level 2, country
            query = query.filter(Admin.admin_level == 2)
            query = query.filter(Admin.name % self.params['country'])
        #sort results
        query = query.order_by(desc(similarity), UnifiedRoad.id)
        return query
    
    def result(self, limit=None, offset=None):
        #check if country was set and at least one row was returned
        if self.query.count() < 1 and self.params['country'] is not None:
            #build a new query without limiting the search by country
            self.params['country'] = None
            self._query = self._build_query()
        
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)
        #get data
        roads = [road for road in self.query]
        #pass results to DictWrapper and calculate additional data
        return DictWrapper(self.__class__.__name__, roads=roads)
    
class OSMQueryCountry(OSMQueryBase):
    """query countries"""
    def is_valid(self):
        if self.params['country'] is None:
            return False
        return True
    
    def _build_query(self):
        similarity = func.similarity(Admin.name, self.params['country'])
        query = self.session.query(Admin)
        query = query.filter(Admin.name % self.params['country'])
        query = query.filter(Admin.admin_level == 2)
        query = query.order_by(desc(similarity), Admin.osm_id)
        return query
    
    def result(self, limit=None, offset=None):
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)
        #get data
        countries = [country for country in self.query]
        #pass results to DictWrapper and calculate additional data
        return DictWrapper(self.__class__.__name__, countries=countries)
    
class OSMQueryPlace(OSMQueryBase):
    """query places"""
    def is_valid(self):
        if self.params['city'] is None:
            return False
        return True
    
    def _build_query(self):
        #check if the input name has suffixes
        if re.search('( [a-z\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f0-9\\(\\)\\\\/-]+ ?)+|/|,', self.params['city']) is not None:
            self._with_suffixes = True
        #check which column shall be part of the query
        place_name_column = LookupPlace.name if self._with_suffixes else LookupPlace.lookup_name
        
        similarity = func.similarity(place_name_column, self.params['city'])
        #query places
        query = self.session.query(LookupPlace)
        #filter data
        query = query.filter(place_name_column % self.params['city'])
        #check if search shall be limited by a country
        if self.params['country'] is not None:
            query = query.join(Admin, functions.intersects(Admin.geometry, LookupPlace.geometry))
            query = query.filter(Admin.admin_level == 2)
            query = query.filter(Admin.name % self.params['country'])
        #sort results
        query = query.order_by(desc(similarity), LookupPlace.osm_id)
        return query
    
    def result(self, limit=None, offset=None):
        #check if country was set and at least one row was returned
        if self.query.count() < 1 and self.params['country'] is not None:
            #build a new query without limiting the search by country
            self.params['country'] = None
            self._query = self._build_query()
        
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)
        #get data
        places = [place for place in self.query]
        #pass results to DictWrapper and calculate additional data
        return DictWrapper(self.__class__.__name__, places=places)
    
class OSMQueryPostcode(OSMQueryBase):
    """query only postcodes"""
    def is_valid(self):
        if self.params['postcode'] is None:
            return False
        return True
    
    def _build_query(self):
        #query postcodes
        query = self.session.query(Postcode)
        #filter data
        query = query.filter(Postcode.postcode == self.params['postcode']) #exact match required
        #check if search shall be limited by a country
        if self.params['country'] is not None:
            query = query.join(Admin, functions.intersects(Admin.geometry, Postcode.geometry))
            query = query.filter(Admin.admin_level == 2)
            query = query.filter(Admin.name % self.params['country'])
        return query
    
    def result(self, limit=None, offset=None):
        #check if country was set and at least one row was returned
        if self.query.count() < 1 and self.params['country'] is not None:
            #build a new query without limiting the search by country
            self.params['country'] = None
            self._query = self._build_query()
        
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)
        #get data
        postcodes = [postcode for postcode in self.query]
        #pass results to DictWrapper and calculate additional data
        return DictWrapper(self.__class__.__name__, postcodes=postcodes)
    
class OSMQueryAddress(OSMQueryBase):
    """query addesses"""
    def is_valid(self):
        """place, street and housenumber must be set"""
        if self.params['housenumber'] is None or self.params['road'] is None or self.params['city'] is None:
            return False
        return True
    
    def _build_query(self):
        #similarity for each column
        street_similarity = func.similarity(Address.street, self.params['road'])
        city_similarity = func.similarity(Address.city, self.params['city'])
        #summarize similarity
        similarity = city_similarity + street_similarity
        #query addresses
        query = self.session.query(Address)
        #filter data
        query = query.filter(Address.street % self.params['road'])
        query = query.filter(Address.city % self.params['city'])
        query = query.filter(Address.housenumber % self.params['housenumber'])
        #check if search shall be limited by a country
        if self.params['country'] is not None:
            query = query.join(Admin, functions.intersects(Admin.geometry, Address.geometry))
            query = query.filter(Admin.admin_level == 2)
            query = query.filter(Admin.name % self.params['country'])
        query = query.order_by(desc(similarity))
        return query
    
    def result(self, limit=None, offset=None):
        #just a few addresses have a country tag, if one is supplied and you get zero results, try again without tag
        if self.query.count() < 1 and self.params['country'] is not None:
            self.params['country'] = None
            self._query = self._build_query()
            
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)
        #get data
        addresses = [address for address in self.query]
        #pass results to DictWrapper and calculate additional data
        return DictWrapper(self.__class__.__name__, addresses=addresses)

class OSMQueryAddressPlaceRoad(OSMQueryBase):
    """query addresses and roads to look for a specific place and road"""
    def is_valid(self):
        if self.params['road'] is None or self.params['city'] is None:
            return False
        return True
        
    def _build_query(self):
        #similarity for each column
        street_similarity = func.similarity(Address.street, self.params['road'])
        city_similarity = func.similarity(Address.city, self.params['city'])
        #summarize similarity
        similarity = city_similarity + street_similarity
        #query addresses
        query = self.session.query(Address)
        #filter data
        query = query.filter(Address.street % self.params['road'])
        query = query.filter(Address.city % self.params['city'])
        #only one address per street and city
        query = query.distinct(Address.city, similarity)
        if self.params['country'] is not None:
            query = query.join(Admin, functions.intersects(Admin.geometry, Address.geometry))
            query = query.filter(Admin.admin_level == 2)
            query = query.filter(Admin.name % self.params['country'])
        query = query.order_by(desc(similarity))
        
        #generate a subquery
        aliased_address = aliased(Address, query.subquery())
        #query roads and addresses
        query = self.session.query(UnifiedRoad, aliased_address)
        #filter data
        buf = functions.buffer(aliased_address.geometry, meter_to_sridunit(aliased_address.geometry.srid, 100))
        query = query.join(aliased_address, functions.intersects(UnifiedRoad.geometry, func.ST_SetSRID(buf, UnifiedRoad.geometry.srid)))
        query = query.filter(UnifiedRoad.name == aliased_address.street)
        return query
        
    def result(self, limit=None, offset=None):
        #check if country was set and at least one row was returned
        if self.query.count() < 1 and self.params['country'] is not None:
            #build a new query without limiting the search by country
            self.params['country'] = None
            self._query = self._build_query()
            
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)
        #get data
        roads = []
        addresses = []
        for road, address in self.query:
            roads.append(road)
            addresses.append(address)
        #pass results to DictWrapper and calculate additional data
        return DictWrapper(self.__class__.__name__, roads=roads, addresses=addresses)

class OSMQueryAdminPlaceRoad(OSMQueryBase):
    """query admin, place and road to look for a specific place and road"""
    def is_valid(self):
        if self.params['road'] is None or self.params['city'] is None:
            return False
        return True
    
    def _build_query(self):
        #check if params['city'] has suffixes
        if re.search('( [a-z\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f0-9\\(\\)\\\\/-]+ ?)+|/|,', self.params['city']) is not None:
            self._with_suffixes = True

        #query the right column
        place_name_column = LookupPlace.name if self._with_suffixes else LookupPlace.lookup_name
        sim_street = func.similarity(UnifiedRoad.name, self.params['road'])
        sim_city = func.similarity(place_name_column, self.params['city'])
        #query roads
        road = self.session.query(UnifiedRoad)
        road = road.filter(UnifiedRoad.name % self.params['road'])
        road = road.order_by(desc(sim_street))
        #query places
        place = self.session.query(LookupPlace)
        place = place.filter(place_name_column % self.params['city'])
        place = place.order_by(desc(sim_city))
        #generate subqueries
        aliased_road = aliased(UnifiedRoad, road.subquery())
        aliased_place = aliased(LookupPlace, place.subquery())
        aliased_place_name_column = aliased_place.name if self._with_suffixes else aliased_place.lookup_name
        aliased_sim_street = func.similarity(aliased_road.name, self.params['road'])
        aliased_sim_city = func.similarity(aliased_place_name_column, self.params['city'])        
        similarity = aliased_sim_city + aliased_sim_street
        #calculate distance between place and road
        distance = functions.distance(aliased_place.geometry, aliased_road.geometry)
        query = self.session.query(Admin, aliased_road, aliased_place)
        #place and road have to intersect the same admin_area
        query = query.join(aliased_road, functions.intersects(Admin.geometry, func.ST_SetSRID(aliased_road.geometry, func.ST_SRID(Admin.geometry))))
        query = query.join(aliased_place, functions.intersects(Admin.geometry, func.ST_SetSRID(aliased_place.geometry, func.ST_SRID(Admin.geometry))))
        query = query.filter(Admin.admin_level == 6)
        
        if self.params['country'] is not None:
            query = query.filter(Admin.admin_level == 2)
            query = query.filter(Admin.name % country)
        query = query.order_by(desc(similarity), distance, aliased_road.id)        
        return query
        
    
    def result(self, limit=None, offset=None):
        #check if country was set and at least one row was returned
        if self.query.count() < 1 and self.params['country'] is not None:
            #build a new query without limiting the search by country
            self.params['country'] = None
            self._query = self._build_query()
            
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)

        #remove duplicate roads - these may occur with this query
        unique_ids = set()
        roads = []
        for admin, road, place in self.query:
            if road.id not in unique_ids:
                unique_ids.add(road.id)
                roads.append(road)
        #pass results to DictWrapper and calculate additional data        
        return DictWrapper(self.__class__.__name__, roads=roads)
    
class OSMQueryPostcodePlaceRoad(OSMQueryBase):
    """query postcodes and places and/or roads"""
    def is_valid(self):
        if self.params['road'] is None and self.params['city'] is None or self.params['postcode'] is None:
            return False
        return True
    
    def _build_query(self):
        sim_city = None
        sim_street = None
        aliased_road = None
        aliased_place = None
        similarity = None
        
        session = meta.Session()
        query = self.session.query(Postcode)
        
        #check if a city is part of the query
        if self.params['city'] is not None:
            if re.search('( [a-z\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f0-9\\(\\)\\\\/-]+ ?)+|/|,', self.params['city']) is not None:
                self._with_suffixes = True
            
            #choose the right column
            place_name_column = LookupPlace.name if self._with_suffixes else LookupPlace.lookup_name
            #similarity
            sim_city = func.similarity(place_name_column, self.params['city'])
            place = self.session.query(LookupPlace)
            place = place.filter(place_name_column % self.params['city'])
            place = place.order_by(desc(sim_city), LookupPlace.osm_id)
            #generate a subquery
            aliased_place = aliased(LookupPlace, place.subquery())
            aliased_place_name_column = aliased_place.name if self._with_suffixes else aliased_place.lookup_name
            sim_city = func.similarity(aliased_place_name_column, self.params['city'])
            #add subquery to output
            query = query.add_entity(aliased_place)
            query = query.join(aliased_place, functions.intersects(Postcode.geometry, func.ST_SetSRID(aliased_place.geometry, func.ST_SRID(Postcode.geometry))))
        
        #check if a road is part of the query
        if self.params['road'] is not None:
            #similarity
            sim_street = func.similarity(UnifiedRoad.name, self.params['road'])
            road = self.session.query(UnifiedRoad)
            road = road.filter(UnifiedRoad.name % self.params['road'])
            road = road.order_by(desc(sim_street), UnifiedRoad.id)
            #generate a subquery
            aliased_road = aliased(UnifiedRoad, road.subquery())
            sim_street = func.similarity(aliased_road.name, self.params['road'])
            #add subquery to output
            query = query.add_entity(aliased_road)
            query = query.join(aliased_road, functions.intersects(Postcode.geometry, func.ST_SetSRID(aliased_road.geometry, func.ST_SRID(Postcode.geometry))))
        #filter the postcode
        query = query.filter(Postcode.postcode == self.params['postcode'])
        
        #check if the search shall be limited by a country
        if self.params['country'] is not None:
            query = query.join(Admin, functions.intersects(Admin.geometry, Postcode.geometry))
            query = query.filter(Admin.admin_level == 2)
            query = query.filter(Admin.name % self.params['country'])
        
        #sort results by distance if both params are given
        if self.params['road'] is not None and self.params['city'] is not None:
            query = query.order_by(functions.distance(aliased_road.geometry, aliased_place.geometry))
        elif sim_street is not None:
            similarity = sim_street
        elif sim_city is not None:
            similarity = sim_city
        #sort results by similarity
        if similarity is not None:
            query = query.order_by(desc(similarity))
        
        return query
    
    def result(self, limit=None, offset=None):
        #check if country was set and at least one row was returned
        if self.query.count() < 1 and self.params['country'] is not None:
            #build a new query without limiting the search by country
            self.params['country'] = None
            self._query = self._build_query()
            
        if limit is not None:
            self._query = self.query.limit(limit)
        
        if offset is not None:
            self._query = self.query.offset(offset)
        
        #store results
        results = []
        postcodes = []
        places = []
        roads = []
        if self.params['road'] is not None and self.params['city'] is not None:
            for postcode, place, road in self.query:
                postcodes.append(postcode)
                places.append(place)
                roads.append(road)
        else:
            if self.params['road'] is not None:
                for postcode, road in self.query:
                    postcodes.append(postcode)
                    roads.append(road)
            else:
                for postcode, place in self.query:
                    postcodes.append(postcode)
                    places.append(place)
                    
        #pass results to DictWrapper and calculate additional data
        return DictWrapper(self.__class__.__name__, postcodes=postcodes, roads=roads, places=places)


def geocode(params, offset=None, previous_query=None):
    #asign all classes 
    address = OSMQueryAddress
    road = OSMQueryRoad
    place = OSMQueryPlace
    postcode = OSMQueryPostcode
    country = OSMQueryCountry
    postcode_sub = OSMQueryPostcodePlaceRoad
    admin_sub = OSMQueryAdminPlaceRoad
    address_sub = OSMQueryAddressPlaceRoad
    
    #will be set by the web-app
    if previous_query:
        previous_queries = previous_query.split(',')
    else:
        previous_queries = []
    
    #set up queue/list
    queries = [address, postcode_sub, address_sub, admin_sub, road, place, postcode, country]
    result = []
    
    for query in queries:
        #initialise class
        osm_query = query(params)
        #check if class can perform a query with the given params
        if osm_query.is_valid():
            
            #only set an offset, if the query-types are the same
            if osm_query.__class__.__name__ in previous_queries:
                wrapper = osm_query.result(5, offset)
            else:
                wrapper = osm_query.result(5, 0)
            #check if any results are present
            if wrapper.has_results():
                #calculate output data
                wrapper.calculate_additional_data()
                result = wrapper.get_results()
                break

    return result
