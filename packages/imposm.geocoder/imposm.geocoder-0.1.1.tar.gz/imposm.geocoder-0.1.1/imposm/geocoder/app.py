
import sys
import os
import imposm.util
from argparse import ArgumentParser
try:
    import simplejson as json
except ImportError:
    import json
from . db.config import DB
from . config import load_config
from . model import init_model, geocode

def main(argv=None):
    parser = ArgumentParser(description='imposm geocoder - search for osm-data', add_help=False)
    parser.add_argument('--help', dest='help', action='store_true', default=False, help='show this help message and exit')
    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    
    prepare_parser = subparsers.add_parser('prepare', add_help=False, help='prepare tables for geocoding')
    prepare_parser.add_argument('--prepare', action='store_true', default=True)
    prepare_parser.add_argument('-m', '--mapping-file', dest='mapping_file', metavar='<file>')
    prepare_parser.add_argument('-h', '--host', dest='host', metavar='<host>')
    prepare_parser.add_argument('-p', '--port', dest='port', metavar='<port>')
    prepare_parser.add_argument('-d', '--database', dest='db', metavar='<dbname>')
    prepare_parser.add_argument('-U', '--user', dest='user', metavar='<user>')
    prepare_parser.add_argument('--connection', dest='connection')
    prepare_parser.add_argument('--proj', dest='proj', metavar='EPSG:900913')
    prepare_parser.add_argument('--table-prefix', dest='table_prefix', default=None, metavar='osm_new_', help='prefix for imported tables')
    prepare_parser.add_argument('--help', dest='help', action='store_true', default='false', help='show this help message and exit')
    
    geocode_parser = subparsers.add_parser('geocode', add_help=False, help='transform an address to coordinates')
    geocode_parser.add_argument('--config', dest='config', metavar='<config file>')
    geocode_parser.add_argument('-r', '--road', default=None, dest='road', metavar='<road name>')
    geocode_parser.add_argument('-n', '--housenumber', default=None, dest='housenumber', metavar='<housenumber>')
    geocode_parser.add_argument('-p', '--postcode', default=None, dest='postcode', metavar='<postal code')
    geocode_parser.add_argument('-c', '--city', default=None, dest='city', metavar='<city name>')
    geocode_parser.add_argument('-x', '--country', default=None, dest='country', metavar='<two letter country code>')
    geocode_parser.add_argument('--help', dest='help', action='store_true', default='false', help='show this help message and exit')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    options = parser.parse_args(argv)

    if options.help:
        if options.command == 'prepare':
            prepare_parser.print_help()
        elif options.command == 'geocode':
            geocode_parser.print_help()
        sys.exit(1)
    
    if options.command == 'prepare':
        mapping_file = os.path.join(os.path.dirname(__file__),
            'defaultmapping.py')
        if options.mapping_file:
            print 'loading %s as mapping' % options.mapping_file
            mapping_file = options.mapping_file
            
        if options.proj:
            if ':' not in options.proj:
                print 'ERROR: --proj should be in EPSG:00000 format'
                sys.exit(1)
            # check proj if meter_to_mapunit needs to do anything
            if options.proj.lower() == 'epsg:4326':
                imposm.mapping.import_srs_is_geographic = True

        mappings = {}
        execfile(mapping_file, mappings)
        db_conf = mappings['db_conf']
        if options.table_prefix:
            db_conf.prefix = options.table_prefix
        else:
            options.table_prefix = db_conf.prefix

        if options.connection:
            from imposm.db.config import db_conf_from_string
            db_conf = db_conf_from_string(options.connection, db_conf)
        else:
            db_conf.host = options.host or db_conf.host
            db_conf.port = options.port or getattr(db_conf, 'port', None) #backw. compat
            if not options.db:
                parser.error('-d/--database is required for this mode')
            db_conf.db = options.db or db_conf.db
            db_conf.user = options.user or db_conf.user
            if options.user:
                from getpass import getpass
                db_conf.password = getpass('password for %(user)s at %(host)s:' % db_conf)
            
            if options.proj:
                db_conf.proj = options.proj
    
        db = DB(db_conf)
        logger = imposm.util.ProgressLog
    
        logger.message('## creating funtions')        
        sql_scripts = [
            os.path.join(os.path.dirname(__file__), 'db/line_merge.sql'),
            os.path.join(os.path.dirname(__file__), 'db/multiline_center.sql'),
        ]        
        db.create_linemerge_functions(sql_scripts)
    
        logger.message('## creating neccessary geocoding tables')
        timer = imposm.util.Timer('generating tables', logger)
        db.create_geometry_union_tables(mappings)
        db.create_geometry_linemerge_tables(mappings)
        timer.stop()        
        db.commit()
        
    if options.command == 'geocode':
        if not options.config:
            parser.error('--config is required for this mode')
        config = load_config(options.config)
        
        init_model(config)
        
        params = {
            'city': options.city,
            'road': options.road,
            'housenumber': options.housenumber,
            'postcode': options.postcode,
            'country': options.country}
        result = geocode(params)
        if result:
            print json.dumps(result, indent=2)
        else:
            print 'nothing found...'
        
if __name__ == "__main__":
    main()