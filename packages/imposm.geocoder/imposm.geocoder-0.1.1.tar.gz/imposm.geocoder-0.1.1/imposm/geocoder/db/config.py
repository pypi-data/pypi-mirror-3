from . postgis import PostGISDBExtended
from imposm.mapping import Options

def DB(db_conf):
    if db_conf.get('name', 'postgis') == 'postgis':
        # default and backwards compat
        return PostGISDBExtended(db_conf)
    raise ValueError('unknown db: %s' % (db_conf.name,))