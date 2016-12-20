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

def calculateNdvi(collectionName, scale, polygon=[], dateFrom=None, dateTo=None):
    """  """
    try:
        plot = ee.Geometry.Polygon(polygon)
        ndviCollection = ee.ImageCollection(collectionName).filterDate(dateFrom, dateTo).select('NDVI')
        def getNdvi(image):
            """  """
            ndviValue = image.reduceRegion(ee.Reducer.mean(), plot, scale).get('NDVI')
            date = image.get('system:time_start')
            ndviImage = ee.Image().set('ndvi', [ndviValue, ee.Number(date)])
            return ndviImage
        ndviCollection1 = ndviCollection.map(getNdvi)
        ndviCollection2 = ndviCollection1.aggregate_array('ndvi')
        values = ndviCollection2.getInfo()
    except EEException as e:
        raise GEEException(e.message)
    return values