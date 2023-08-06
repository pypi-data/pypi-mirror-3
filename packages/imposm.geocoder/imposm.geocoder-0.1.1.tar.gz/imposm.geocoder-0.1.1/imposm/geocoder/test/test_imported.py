# Copyright 2012 Omniscale (http://omniscale.com)
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
import os
import tempfile
import shutil

from contextlib import contextmanager

import imposm.app
import imposm.mapping
import imposm.geocoder.app
import imposm.geocoder.db.config
import imposm.geocoder.mapping

from nose.tools import eq_
from nose.plugins import skip

temp_dir = None
old_cwd = None

try:
    from imposm_test_conf import db_conf
    db_conf = imposm.mapping.Options(db_conf)
except ImportError:
    raise skip.SkipTest('no imposm_test_conf.py with db_conf found')

def setup_module():
    global old_cwd, temp_dir
    old_cwd = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    test_osm_file = os.path.join(os.path.dirname(__file__), 'test.osm')
    mapping_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'geocodemapping.py')
    with capture_out():
        imposm.app.main(['--read', test_osm_file, '--write', '-d', db_conf.db,
            '--host', db_conf.host, '--proj', db_conf.proj, '-m', mapping_file,
            '--table-prefix', db_conf.prefix])
        imposm.geocoder.app.main(['prepare', '-d', db_conf.db, '-h', db_conf.host,
            '-m', mapping_file, '--table-prefix', db_conf.prefix, '--proj', db_conf.proj])


class TestCreated(object):
    def __init__(self):
        self.db = imposm.geocoder.db.config.DB(db_conf)
        
    def test_merged_roads_count(self):
        cur = self.db.cur
        cur.execute('select count(*) from osm_test_roads_merged')
        results = cur.fetchall()
        eq_(len(results), 1)
        eq_(results[0][0], 8)
        
    def test_unified_postcodes_count(self):
        cur = self.db.cur
        cur.execute('select count(*) from osm_test_postcodes_union')
        results = cur.fetchall()
        eq_(len(results), 1)
        eq_(results[0][0], 4)
        

def teardown_module():
    if old_cwd:
        os.chdir(old_cwd)
    
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    

@contextmanager
def capture_out():
    import sys
    from cStringIO import StringIO

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
