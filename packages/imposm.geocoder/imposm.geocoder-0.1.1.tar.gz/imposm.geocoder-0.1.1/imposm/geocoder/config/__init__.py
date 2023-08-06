from __future__ import with_statement

import os
from ConfigParser import RawConfigParser

class GeocoderConfig(object):
    def __init__(self, config):
        self.database = None
        self.tablenames = {}
        self.srid = 900913
        self.config = config
        self._set_attributes()
        
    def _set_attributes(self):
        if self.config.has_section('database'):
            self.database = '%s://%s:%s@%s/%s' % (self.config.get('database','dialect'),
                                                  self.config.get('database','user'),
                                                  self.config.get('database','password'),
                                                  self.config.get('database','host'),
                                                  self.config.get('database','dbname'))
        if self.config.has_section('tablenames'):
            self.tablenames['places'] = self.config.get('tablenames', 'places')
            self.tablenames['roads'] = self.config.get('tablenames', 'roads')
            self.tablenames['addresses'] = self.config.get('tablenames', 'addresses')
            self.tablenames['postcodes'] = self.config.get('tablenames', 'postcodes')
            self.tablenames['admin'] = self.config.get('tablenames', 'admin')
            
        if self.config.has_section('projection'):
            # TODO raise exception, if option does not exist
            self.srid = int(self.config.get('projection', 'srs').split(':')[1])
        
    def _check_config(self):
        pass

def load_config(filename):
    """
    Read the config file and return an object
    """
    if os.path.exists(filename):
        if isinstance(filename, basestring):
            config = RawConfigParser()
            files_read = config.read(filename)
            if filename in files_read:
                return GeocoderConfig(config)
    #TODO raise error?
            
#TODO check conf-settings
    
