import ee
from ee.ee_exception import EEException

from gee_exception import GEEException

def imageToMapId(imageName, visParams={}):
    """  """
    try:
        eeImage = ee.Image(imageName)
        mapId = eeImage.getMapId(visParams)
        values = {
            'mapid': mapId['mapid'],
            'token': mapId['token']
        }
    except EEException as e:
        raise GEEException(e.message)
    return values

def firstImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
        eeCollection = ee.ImageCollection(collectionName)
        if (dateFrom and dateTo):
            eeFilterDate = ee.Filter.date(dateFrom, dateTo)
            eeCollection = eeCollection.filter(eeFilterDate)
        eeFirstImage = ee.Image(eeCollection.first());
        values = imageToMapId(eeFirstImage, visParams)
    except EEException as e:
        raise GEEException(e.message)
    return values

def getTimeSeriesByCollectionAndIndex(collectionName, indexName, scale, coords=[], dateFrom=None, dateTo=None):
    """  """
    try:
        geometry = None
        if isinstance(coords[0], list):
            geometry = ee.Geometry.Polygon(coords)
        else:
            geometry = ee.Geometry.Point(coords)
        indexCollection = ee.ImageCollection(collectionName).filterDate(dateFrom, dateTo).select(indexName)
        def getIndex(image):
            """  """
            indexValue = image.reduceRegion(ee.Reducer.mean(), geometry, scale).get(indexName)
            date = image.get('system:time_start')
            indexImage = ee.Image().set('indexValue', [indexValue, ee.Number(date)])
            return indexImage
        indexCollection1 = indexCollection.map(getIndex)
        indexCollection2 = indexCollection1.aggregate_array('indexValue')
        values = indexCollection2.getInfo()
    except EEException as e:
        raise GEEException(e.message)
    return values

def getTimeSeriesByIndex(indexName, scale, coords=[]):
    """  """
    try:
        geometry = None
        if isinstance(coords[0], list):
            geometry = ee.Geometry.Polygon(coords)
        else:
            geometry = ee.Geometry.Point(coords)
        bands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask']
        bandsByCollection = {
            'LANDSAT/LC8_SR': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'cfmask'],
            'LANDSAT/LC8_SR': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'cfmask'],
            'LANDSAT/LE7_SR': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'cfmask'],
            'LANDSAT/LT5_SR': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'cfmask'],
            'LANDSAT/LT4_SR': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'cfmask']
        }
        indexes = {
            'NDVI': '(i.nir - i.red) / (i.nir + i.red)',
            'EVI': '2.5 * (i.nir - i.red) / (i.nir + 6.0 * i.red - 7.5 * i.blue + 1)',
            'EVI2': '2.5 * (i.nir - i.red) / (i.nir + 2.4 * i.red + 1)',
            'NDWI': '(i.nir - i.swir1) / (i.nir + i.swir1)'
        }
        def getExpression(image):
            """  """
            time = ee.Number(image.get('system:time_start'))
            image = image.select(bandsByCollection[collectionName], bands).divide(10000)
            return image.expression(indexes[indexName], {'i': image}).rename(['index']).addBands(image.select(['cfmask']).add(1)).set('system:time_start', time)
        def transformRow(row):
            """  """
            row = ee.List(row)
            time = row.get(3)
            index = row.get(4)
            cfmask = row.get(5)
            return ee.Algorithms.If(cfmask, ee.Algorithms.If(ee.Number(cfmask).eq(1), ee.List([index, time]), None), None)
        collectionNames = bandsByCollection.keys()
        collectionName = collectionNames[0]
        collection = ee.ImageCollection(collectionNames[0]).sort('system:time_start').filterBounds(geometry).map(getExpression)
        for i, val in enumerate(collectionNames[1:], start=1):
            collectionName = collectionNames[i]
            collectionToMerge = ee.ImageCollection(collectionNames[i]).sort('system:time_start').filterBounds(geometry).map(getExpression)
            collection = ee.ImageCollection(collection.merge(collectionToMerge))
        values = ee.ImageCollection(collection.sort('system:time_start').distinct('system:time_start')).getRegion(geometry, 30).slice(1).map(transformRow).removeAll([None])
        values = values.getInfo()
    except EEException as e:
        raise GEEException(e.message)
    return values

def getStatistics(paramType, aOIPoly):
    values = {}
    if (paramType == 'basin'):
      basinFC = ee.FeatureCollection('ft:1aIbTi69cXMMIm5ZvHNC67hVmhefPDLfEat15iike')
      basin = basinFC.filter(ee.Filter.eq('SubBasin', aOIPoly)).first();
      poly = basin.geometry()
    elif (paramType == 'landscape'):
      lscapeFC = ee.FeatureCollection('ft:1XuZH2r-oai_knDgWiOUxyDjlHZQKsEZChOjGsTjr')
      landscape = lscapeFC.filter(ee.Filter.eq('NAME', aOIPoly)).first();
      poly = landscape.geometry()
    else:
      poly = ee.Geometry.Polygon(aOIPoly)
    elev = ee.Image('USGS/GTOPO30')
    minmaxElev = elev.reduceRegion(ee.Reducer.minMax(), poly, 1000, maxPixels=500000000)
    minElev = minmaxElev.get('elevation_min').getInfo()
    maxElev = minmaxElev.get('elevation_max').getInfo()
    ciesinPopGrid = ee.Image('CIESIN/GPWv4/population-count/2015')
    popDict = ciesinPopGrid.reduceRegion(ee.Reducer.sum(), poly, maxPixels=500000000)
    pop = popDict.get('population-count').getInfo()
    pop = int(pop) 
    values = {
        'minElev': minElev,
        'maxElev': maxElev,
        'pop': pop
    }
    return values