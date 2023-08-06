
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