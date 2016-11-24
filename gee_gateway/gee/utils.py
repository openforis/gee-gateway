import ee
from ee.ee_exception import EEException

def visParamsBuilder(Min, Max, bands):
    """  """
    visParams = {}
    if Min and Max and Min < Max:
        visParams['min'] = Min
        visParams['max'] = Max
    visParams['bands'] = bands
    return visParams

def imageToMapId(imageName, visParams={}):
    """  """
    try:
        image = ee.Image(imageName)
        mapId = image.getMapId(visParams)
        values = {
            'mapid': mapId['mapid'],
            'token': mapId['token']
        }
    except EEException as e:
        values = {
            'errMsg': e.message
        }
    return values

def fistImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
        collection = ee.ImageCollection(collectionName)
        if (dateFrom and dateTo):
            filterDate = ee.Filter.date(dateFrom, dateTo)
            collection.filter(filterDate)
        firstImage = ee.Image(collection.first());
        values = imageToMapId(firstImage, visParams)
    except EEException as e:
        values = {
            'errMsg': e.message
        }
    return values