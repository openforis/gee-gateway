import datetime
import json

import dateutil.parser
import requests
from shapely.geometry import CAP_STYLE
from shapely.geometry import Polygon
from shapely_geojson import dumps

global PLANET_API_KEY
global session

def map_bounds(geometry):
    bounds = geometry.bounds
    return [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]

def p(data):
    print(json.dumps(data, indent=2))

def pick(dictionary, keys):
    return dict((k, dictionary.get(k)) for k in keys)

def feature_date(feature):
    return dateutil.parser.parse(feature['properties']['acquired']).strftime('%Y-%m-%d')

def distinct_date(features):
    dates = []
    result = []
    for feature in features:
        date = feature_date(feature)
        if not date in dates:
            dates.append(date)
            result.append(feature)
    return result

def date_filter(start, end):
    return {
        'type': 'DateRangeFilter',
        'field_name': 'acquired',
        'config': {
            'gte': start,
            'lt': end
        }
    }

def within_days_filter(feature, days):
    date = dateutil.parser.parse(feature['properties']['acquired'])
    start = (date - datetime.timedelta(days=days - 1)).strftime('%Y-%m-%d') + 'T00:00:00.000Z'
    end = (date + datetime.timedelta(days=days)).strftime('%Y-%m-%d') + 'T23:59:59.000Z'
    return date_filter(start, end)

def geometry_filter(geometry):
    return {
        'type': 'GeometryFilter',
        'field_name': 'geometry',
        'config': json.loads(dumps(geometry))
    }

def string_filter(field_name, strings):
    return  {
        'type':'StringInFilter',
        'field_name': field_name,
        'config': strings
    }

# The quality of a feature. Use clear_percent, with cloud_cover as a fallback
def quality(feature):
    p = feature['properties']
    quality = p.get('clear_percent')  # clear_percent [0, 100] only exist on newer features
    if quality is not None:
        return quality
    else:
        # cloud_cover [0, 1] is really not very accurate and misses a lot of clouds.
        # Therefore we weight it a bit lower than clear_percent
        return (1 - p['cloud_cover']) * 50

def search(item_types, filters,  sort=False):
    and_filter = {
        'type': 'AndFilter',
        'config': filters
    }
    request = {
        'item_types' : item_types,
        'filter' : and_filter
    }

    def next_page(res_json):
        features = res_json.get('features')
        links = res_json.get('_links')
        if links and links['_next']:
            next_url = links['_next']
            res = requests.get(next_url, auth=(PLANET_API_KEY, ''))
            if res.status_code >= 400:
                raise ValueError('Error searching Planet. HTTP {}: {}'.format(res.status_code, res.reason))
            next_features = next_page(res.json())
            return features + next_features
        else:
            return features
    res = session.post('https://api.planet.com/data/v1/quick-search', json=request)
    if res.status_code >= 400:
        raise ValueError('Error searching Planet. HTTP {}: {}'.format(res.status_code, res.reason))
    # There is unfortunately no ability to request sorted feature, so we have to get them all then sort them ourselves.
    # This means a whole lot of paging for long date-ranges. We might want to limit this...
    # We asked for them to implement the sorting, and they said they will.
    # We also asked for the ability to limit which metadata to return for each feature.
    features = next_page(res.json())
    if sort:
        return list(sorted(features, key=lambda f: quality(f) , reverse=True))
    else:
        return features

def features_layer(features, name='Planet'):
    ids = [feature['properties']['item_type'] + ':' + feature['id'] for feature in features]
    # Request a tile URL for the feature ids. Unfortunately, we have no control over tile ordering in the resulting
    # tiles. This is something we asked for, so we can put best quality features at the top
    res = requests.post(
        'https://tiles0.planet.com/data/v1/layers',
        auth=(PLANET_API_KEY, ''),
        data={'ids': ', '.join(ids)}
    )
    if res.status_code >= 400:
        raise ValueError('Error creating Planet tile. HTTP {}: {}'.format(res.status_code, res.reason))
    layer = res.json()['name']
    return {"date": feature_date(features[0]), "layerID": layer}

# Add a layer with features similar to one the requested one.
def add_similar_features(feature, geometry):
    features = search(
        item_types=[feature['properties']['item_type']],
        filters=[
            geometry_filter(geometry.buffer(0.5, cap_style=CAP_STYLE.square)),  # Close by
            within_days_filter(feature, 1),  # Same day
            string_filter('instrument', [feature['properties']['instrument']])  # Same instrument
        ],
        sort=False
    )
    name = feature_date(feature)
    return features_layer(features, name)

def getPlanetMapID(api_key, geometry, start, end=None, layerCount=1, item_types=['PSScene3Band', 'PSScene4Band']):
    fullList = []
    global PLANET_API_KEY
    PLANET_API_KEY = api_key
    global session
    session = requests.Session()
    session.auth = (PLANET_API_KEY, '')
    fend = ''
    if end is None:
        fend = start + 'T23:59:59.000Z'
    else:
        fend = end + 'T00:00:00.000Z'
    fstart = start + 'T00:00:00.000Z'
    print("fstart: " + fstart)
    print("fend: " + fend)
    features = search(  # Scenes in date range, intersecting the geometry centroid, sorted by quality
        item_types=item_types,
        filters=[
            date_filter(fstart, fend), #date_filter(start, end),
            geometry_filter(Polygon(geometry)),
            string_filter('quality_category', ['standard'])
        ],
        sort=True
    )
    best_features = distinct_date(features)[0:layerCount]  # The best n features with distinct date, sorted by quality
    for feature in best_features[::-1]:  # Reverse the sorting and iterate
        fullList.append(add_similar_features(feature, Polygon(geometry).centroid))
    if len(fullList) == 0:
        fullList.append({"date": "null", "layerID": "null"})
    return fullList