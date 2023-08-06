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

from __future__ import with_statement

import time
import os

import psycopg2
import psycopg2.extensions

import logging
log = logging.getLogger(__name__)

from imposm import config
from imposm.db.postgis import PostGISDB, PostGISGeneralizedTable
from .. mapping import GeometryLineMergeTable, GeometryUnionTable

class PostGISDBExtended(PostGISDB):
    def create_geometry_union_tables(self, mappings):
        mappings = [m for m in mappings.values() if isinstance(m, GeometryUnionTable)]
        for mapping in sorted(mappings, key=lambda x: x.name, reverse=True):
            PostGISGeometryUnionTable(self, mapping).create()
        
    def create_geometry_linemerge_tables(self, mappings):
        mappings = [m for m in mappings.values() if isinstance(m, GeometryLineMergeTable)]
        for mapping in sorted(mappings, key=lambda x: x.name, reverse=True):
            PostGISGeometryLineMergeTable(self, mapping).create()
            
    def create_linemerge_functions(self, sql_scripts):
        cur = self.connection.cursor()
        for script in sql_scripts:
            if os.path.exists(script):
                with open(script, 'r') as f:
                    cur.execute(f.read())
                    self.commit()

class PostGISGeometryUnionTable(PostGISGeneralizedTable):
    def _stmt(self):
        if config.imposm_pg_serial_id:
            serial_column = "id SERIAL PRIMARY KEY,"
        else:
            serial_column = ""
    
        return """
                CREATE TABLE "%s" (
                    %s
                    postcode VARCHAR(255),
                    geometry GEOMETRY
                 );
                """ % (self.table_name, serial_column)
    
    def _union_insert_stmt(self):
        if self.mapping.group_by:
            group_by = ' GROUP BY ' + self.mapping.group_by
        else:
            group_by = ''
        
        return """INSERT INTO %s(postcode, geometry) SELECT %s, ST_UNION(geometry) FROM %s%s""" % (self.table_name, self.mapping.group_by, self.db.to_tablename(self.mapping.origin.name), group_by)
    
    def _trgm_idx_stmt(self):
        return """CREATE INDEX %(tablename)s_trgm_idx_%(column)s ON "%(tablename)s" USING GIST (%(column)s gist_trgm_ops)""" % dict(tablename=self.table_name, column='postcode')
        
    def create(self):
        cur = self.db.connection.cursor()
        cur.execute('BEGIN')
        try:
            cur.execute('SAVEPOINT pre_drop_table')
            cur.execute('DROP TABLE "%s" CASCADE' % (self.table_name, ))
        except psycopg2.ProgrammingError:
            cur.execute('ROLLBACK TO SAVEPOINT pre_drop_table')
        
        cur.execute(self._stmt())
        cur.execute(self._union_insert_stmt())
        cur.execute(self._idx_stmt())
        cur.execute(self._trgm_idx_stmt())

        cur.execute('SELECT * FROM geometry_columns WHERE f_table_name = %s', (self.table_name, ))
        if cur.fetchall():
            # drop old entry to handle changes of SRID
            cur.execute('DELETE FROM geometry_columns WHERE f_table_name = %s', (self.table_name, ))
        cur.execute(self._geom_table_stmt())
        
class PostGISGeometryLineMergeTable(PostGISGeneralizedTable):
    def _stmt(self):
        if config.imposm_pg_serial_id:
            serial_column = "id SERIAL PRIMARY KEY,"
        else:
            serial_column = ""
    
        return """
                CREATE TABLE "%s" (
                    %s
                    name VARCHAR(255),
                    osm_ids INT4[],
                    geometry GEOMETRY
                 );
                """ % (self.table_name, serial_column)
    
    def _insert_stmt(self):
        if self.mapping.group_by:
            group_by = ' GROUP BY ' + self.mapping.group_by
        else:
            group_by = ''
        where = " WHERE name IS NOT NULL or name <> ''"
        
        return """INSERT INTO %s(name, osm_ids, geometry) SELECT name, (merged).osm_ids, (merged).geom FROM (SELECT %s AS name, multiline_merge(st_linemerge(st_collect(geometry)), array_agg(osm_id)) AS merged FROM %s%s%s) AS subquery""" % (self.table_name, self.mapping.group_by, self.db.to_tablename(self.mapping.origin.name), where, group_by)
        
    def _trgm_idx_stmt(self):
        return """CREATE INDEX %(tablename)s_trgm_idx_%(column)s ON "%(tablename)s" USING GIST (%(column)s gist_trgm_ops)""" % dict(tablename=self.table_name, column='name')
        
    def create(self):
        cur = self.db.connection.cursor()
        cur.execute('BEGIN')
        try:
            cur.execute('SAVEPOINT pre_drop_table')
            cur.execute('DROP TABLE "%s" CASCADE' % (self.table_name, ))
        except psycopg2.ProgrammingError:
            cur.execute('ROLLBACK TO SAVEPOINT pre_drop_table')
        
        cur.execute(self._stmt())
        cur.execute(self._insert_stmt())
        cur.execute(self._idx_stmt())
        cur.execute(self._trgm_idx_stmt())

        cur.execute('SELECT * FROM geometry_columns WHERE f_table_name = %s', (self.table_name, ))
        if cur.fetchall():
            # drop old entry to handle changes of SRID
            cur.execute('DELETE FROM geometry_columns WHERE f_table_name = %s', (self.table_name, ))
        cur.execute(self._geom_table_stmt())        
