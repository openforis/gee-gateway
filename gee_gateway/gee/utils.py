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

def fistImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
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

def getTimeSeriesByIndex(collectionName, indexName, scale, polygon=[], dateFrom=None, dateTo=None):
    """  """
    try:
        plot = ee.Geometry.Polygon(polygon)
        indexCollection = ee.ImageCollection(collectionName).filterDate(dateFrom, dateTo).select(indexName)
        def getIndex(image):
            """  """
            indexValue = image.reduceRegion(ee.Reducer.mean(), plot, scale).get(indexName)
            date = image.get('system:time_start')
            indexImage = ee.Image().set('indexValue', [indexValue, ee.Number(date)])
            return indexImage
        indexCollection1 = indexCollection.map(getIndex)
        indexCollection2 = indexCollection1.aggregate_array('indexValue')
        values = indexCollection2.getInfo()
    except EEException as e:
        raise GEEException(e.message)
    return values