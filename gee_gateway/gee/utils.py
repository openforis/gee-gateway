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

def getTimeSeriesByIndex(collectionName, indexName, scale, coords=[], dateFrom=None, dateTo=None):
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