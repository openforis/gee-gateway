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
def firstCloudFreeImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
        print('collectionName ' + collectionName)
        skipCloudMask = False
        eeCollection = ee.ImageCollection(collectionName)
        if("b2" not in visParams["bands"].lower()):
            skipCloudMask = True
        elif ("lc8" in collectionName.lower()):
            skipCloudMask = False
        elif ("le7" in collectionName.lower()):
            skipCloudMask = False
        elif ("lt5" in collectionName.lower()):
            skipCloudMask = False 
        else:
            skipCloudMask = True
        if (dateFrom and dateTo):
            eeFilterDate = ee.Filter.date(dateFrom, dateTo)
            eeCollection = eeCollection.filter(eeFilterDate)
        eeFirstImage = ee.Image(eeCollection.first());
        try:
            if(skipCloudMask == False):
                sID = ''
                if ("lc8" in collectionName.lower()):
                    sID = 'OLI_TIRS'
                elif ("le7" in collectionName.lower()):
                   sID = 'ETM'
                elif ("lt5" in collectionName.lower()):
                    sID = 'TM'            
                scored = ee.Algorithms.Landsat.simpleCloudScore(eeFirstImage.set('SENSOR_ID', sID))
                mask = scored.select(['cloud']).lte(20)
                masked = eeFirstImage.updateMask(mask)
                
                values = imageToMapId(masked, visParams)
            else:
                values = imageToMapId(eeFirstImage, visParams)
        except EEException as ine:
            imageToMapId(eeFirstImage, visParams)
    except EEException as e:
        print(visParams)
        raise GEEException(e.message)
    return values
def filteredImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
        eeCollection = ee.ImageCollection(collectionName)
        if (dateFrom and dateTo):
            eeFilterDate = ee.Filter.date(dateFrom, dateTo)
            eeCollection = eeCollection.filter(eeFilterDate)
        eeFirstImage = ee.Image(eeCollection.mean());
        values = imageToMapId(eeFirstImage, visParams)
    except EEException as e:
        raise GEEException(e.message)
    return values

def getTimeSeriesByIndex(collectionName, indexName, scale, polygon=[], dateFrom=None, dateTo=None, reducer=None):
    """  """
    try:
        plot = ee.Geometry.Polygon(polygon)
        indexCollection = ee.ImageCollection(collectionName).filterDate(dateFrom, dateTo).select(indexName)
        def getIndex(image):
            """  """
            theReducer = None;
            if(reducer == 'min'):
                theReducer = ee.Reducer.min()
            elif (reducer == 'max'):
                theReducer = ee.Reducer.max()
            else:
                theReducer = ee.Reducer.mean()
            indexValue = image.reduceRegion(theReducer, plot, scale).get(indexName)
            date = image.get('system:time_start')
            indexImage = ee.Image().set('indexValue', [indexValue, ee.Number(date)])
            return indexImage
        indexCollection1 = indexCollection.map(getIndex)
        indexCollection2 = indexCollection1.aggregate_array('indexValue')
        values = indexCollection2.getInfo()
    except EEException as e:
        raise GEEException(e.message)
    return values
def cloudMaskGetTimeSeriesByIndex(collectionName, indexName, scale, polygon=[], dateFrom=None, dateTo=None, reducer=None):
    """  """
    try:
        plot = ee.Geometry.Polygon(polygon)
        indexCollection = ee.ImageCollection(collectionName).filterDate(dateFrom, dateTo).select(indexName)
        def getIndex(image):
            """  """
            theReducer = None;
            if(reducer == 'min'):
                theReducer = ee.Reducer.min()
            elif (reducer == 'max'):
                theReducer = ee.Reducer.max()
            else:
                theReducer = ee.Reducer.mean()
            sID = ''
            if ("lc8" in collectionName.lower()):
               sID = 'OLI_TIRS'
            elif ("le7" in collectionName.lower()):
               sID = 'ETM'
            elif ("lt5" in collectionName.lower()):
                sID = 'TM'            
            scored = ee.Algorithms.Landsat.simpleCloudScore(image.set('SENSOR_ID', sID))
            mask = scored.select(['cloud']).lte(20)
            masked = image.updateMask(mask)                
            indexValue = masked.reduceRegion(theReducer, plot, scale).get(indexName)
            date = masked.get('system:time_start')
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