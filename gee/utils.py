import datetime
import ee
from ee.ee_exception import EEException
from gee.gee_exception import GEEException
from itertools import groupby
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import math
import numpy as np
import sys
import gee.inputs

logger = logging.getLogger(__name__)
handler = RotatingFileHandler('gee-gateway-nginx.log', maxBytes=10485760, backupCount=10)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def initialize(ee_account='', ee_key_path='', ee_user_token=''):
    try:
        if ee_account and ee_key_path:
            try:
                credentials = ee.ServiceAccountCredentials(ee_account, ee_key_path)
                ee.Initialize(credentials)

            except EEException as e:
                print(str(e))
        else:
            raise Exception("EE Initialize error", "No credentials found")
    except (EEException, TypeError) as e:
        logger.error("******EE initialize error************", sys.exc_info()[0])
        pass

def imageToMapId(imageName, visParams={}):
    """  """
    try:
        logger.error('******imageToMapId************')
        eeImage = ee.Image(imageName)
        mapId = eeImage.getMapId(visParams)
        logger.error('******imageToMapId complete************')
        values = {
            'mapid': mapId['mapid'],
            'token': mapId['token'],
            'url': mapId['tile_fetcher'].url_format
        }
    except EEException as e:
        logger.error("******imageToMapId error************", sys.exc_info()[0])
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
        raise GEEException(sys.exc_info()[0])
    return values

def meanImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
        eeCollection = ee.ImageCollection(collectionName)
        if (dateFrom and dateTo):
            eeFilterDate = ee.Filter.date(dateFrom, dateTo)
            eeCollection = eeCollection.filter(eeFilterDate)
        eeMeanImage = ee.Image(eeCollection.mean());
        values = imageToMapId(eeMeanImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def firstCloudFreeImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
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
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
        eeCollection = ee.ImageCollection(collectionName)
        if (dateFrom and dateTo):
            eeFilterDate = ee.Filter.date(dateFrom, dateTo)
            eeCollection = eeCollection.filter(eeFilterDate)
        eeFirstImage = ee.Image(eeCollection.mosaic());
        values = imageToMapId(eeFirstImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def getImageCollectionAsset(collectionName, visParams={}):
    try:
        eeCollection = ee.ImageCollection(collectionName)
        values = imageToMapId(eeCollection.mosaic(), visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageByIndexToMapId(iniDate=None, endDate=None, index='NDVI'):
    """  """
    try:
        if (index == 'NDVI'):
            values = filteredImageNDVIToMapId(iniDate, endDate)
        elif (index == 'EVI'):
            values = filteredImageEVIToMapId(iniDate, endDate)
        elif (index == 'EVI2'):
            values = filteredImageEVI2ToMapId(iniDate, endDate)
        elif (index == 'NDMI'):
            values = filteredImageNDMIToMapId(iniDate, endDate)
        elif (index == 'NDWI'):
            values = filteredImageNDWIToMapId(iniDate, endDate)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageNDVIToMapId(iniDate=None, endDate=None,outCollection=False):
    """  """
    def calcNDVI(img):
        return img.expression('(i.nir - i.red) / (i.nir + i.red)',  {'i': img}).rename(['NDVI'])\
                .set('system:time_start',img.get('system:time_start'))
    try:
        eeCollection = getLandSatMergedCollection().filterDate(iniDate,endDate) #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='c9c0bf,435ebf,eee8aa,006400'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        if outCollection:
            values = eeCollection.map(calcNDVI)
        else:
            eviImage = ee.Image(eeCollection.map(calcNDVI).mean())
            values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageEVIToMapId(iniDate=None, endDate=None,outCollection=False):
    """  """
    def calcEVI(img):
        return img.expression('2.5 * (i.nir - i.red) / (i.nir + 6.0 * i.red - 7.5 * i.blue + 1)',  {'i': img}).rename(['EVI'])\
                .set('system:time_start',img.get('system:time_start'))
    try:
        eeCollection = getLandSatMergedCollection().filterDate(iniDate,endDate) #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='F5F5F5,E6D3C5,C48472,B9CF63,94BF3D,6BB037,42A333,00942C,008729,007824,004A16'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        if outCollection:
            values = eeCollection.map(calcEVI)
        else:
            eviImage = ee.Image(eeCollection.map(calcEVI).mean())
            values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageEVI2ToMapId(iniDate=None, endDate=None,outCollection=False):
    """  """
    def calcEVI2(img):
        return img.expression('2.5 * (i.nir - i.red) / (i.nir + 2.4 * i.red + 1)',  {'i': img}).rename(['EVI2'])\
                .set('system:time_start',img.get('system:time_start'))
    try:
        eeCollection = getLandSatMergedCollection().filterDate(iniDate,endDate) #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='F5F5F5,E6D3C5,C48472,B9CF63,94BF3D,6BB037,42A333,00942C,008729,007824,004A16'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        if outCollection:
            values = eeCollection.map(calcEVI2)
        else:
            eviImage = ee.Image(eeCollection.map(calcEVI2).mean())
            values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageNDMIToMapId(iniDate=None, endDate=None,outCollection=False):
    """  """
    def calcNDMI(img):
        return img.expression('(i.nir - i.swir1) / (i.nir + i.swir1)',  {'i': img}).rename(['NDMI'])\
                .set('system:time_start',img.get('system:time_start'))
    try:
        eeCollection = getLandSatMergedCollection().filterDate(iniDate,endDate) #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='0000FE,2E60FD,31B0FD,00FEFE,50FE00,DBFE66,FEFE00,FFBB00,FF6F00,FE0000'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        if outCollection:
            values = eeCollection.map(calcNDMI)
        else:
            eviImage = ee.Image(eeCollection.map(calcNDMI).mean())
            values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageNDWIToMapId(iniDate=None, endDate=None,outCollection=False):
    """  """
    def calcNDWI(img):
        return img.expression('(i.green - i.nir) / (i.green + i.nir)',  {'i': img}).rename(['NDWI'])\
                .set('system:time_start',img.get('system:time_start'))
    try:
        eeCollection = getLandSatMergedCollection().filterDate(iniDate,endDate) #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='505050,E8E8E8,00FF33,003300'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        if outCollection:
            values = eeCollection.map(calcNDWI)
        else:
            eviImage = ee.Image(eeCollection.map(calcNDWI).mean())
            values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def getLandSatMergedCollection():
    eeCollection = None
    try:
        sensorBandDictLandsatTOA = {'L8': [1,2,3,4,5,9,6],
                                    'L7': [0,1,2,3,4,5,7],
                                    'L5': [0,1,2,3,4,5,6],
                                    'L4': [0,1,2,3,4,5,6],
                                    'S2': [1,2,3,7,11,10,12]}
        bandNamesLandsatTOA = ['blue','green','red','nir','swir1','temp','swir2']
        metadataCloudCoverMax = 100
        #region = ee.Geometry.Point([5.2130126953125,15.358356179450585])
        #.filterBounds(region).filterDate(iniDate,endDate)\
        lt4 = ee.ImageCollection('LANDSAT/LT4_L1T_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L4'],bandNamesLandsatTOA).map(lsMaskClouds)
        lt5 = ee.ImageCollection('LANDSAT/LT5_L1T_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L5'],bandNamesLandsatTOA).map(lsMaskClouds)
        le7 = ee.ImageCollection('LANDSAT/LE7_L1T_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L7'],bandNamesLandsatTOA).map(lsMaskClouds)
        lc8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L8'],bandNamesLandsatTOA).map(lsMaskClouds)
        s2 = ee.ImageCollection('COPERNICUS/S2')\
            .filterMetadata('CLOUDY_PIXEL_PERCENTAGE','less_than',metadataCloudCoverMax)\
            .map(s2MaskClouds).select(sensorBandDictLandsatTOA['S2'],bandNamesLandsatTOA)\
            .map(bandPassAdjustment)
        eeCollection = ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8).merge(s2))
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return eeCollection

def lsMaskClouds(img,cloudThresh=10):
    score = ee.Image(1.0);
    # Clouds are reasonably bright in the blue band.
    blue_rescale = img.select('blue').subtract(ee.Number(0.1)).divide(ee.Number(0.3).subtract(ee.Number(0.1)))
    score = score.min(blue_rescale);

    # Clouds are reasonably bright in all visible bands.
    visible = img.select('red').add(img.select('green')).add(img.select('blue'))
    visible_rescale = visible.subtract(ee.Number(0.2)).divide(ee.Number(0.8).subtract(ee.Number(0.2)))
    score = score.min(visible_rescale);

    # Clouds are reasonably bright in all infrared bands.
    infrared = img.select('nir').add(img.select('swir1')).add(img.select('swir2'))
    infrared_rescale = infrared.subtract(ee.Number(0.3)).divide(ee.Number(0.8).subtract(ee.Number(0.3)))
    score = score.min(infrared_rescale);

    # Clouds are reasonably cool in temperature.
    temp_rescale = img.select('temp').subtract(ee.Number(300)).divide(ee.Number(290).subtract(ee.Number(300)))
    score = score.min(temp_rescale);

    # However, clouds are not snow.
    ndsi = img.normalizedDifference(['green', 'swir1']);
    ndsi_rescale = ndsi.subtract(ee.Number(0.8)).divide(ee.Number(0.6).subtract(ee.Number(0.8)))
    score =  score.min(ndsi_rescale).multiply(100).byte();
    mask = score.lt(cloudThresh).rename(['cloudMask']);
    img = img.updateMask(mask);
    return img.addBands(score);

def s2MaskClouds(img):
  qa = img.select('QA60');

  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloudBitMask = int(math.pow(2, 10));
  cirrusBitMask = int(math.pow(2, 11));

  # clear if both flags set to zero.
  clear = qa.bitwiseAnd(cloudBitMask).eq(0).And(
             qa.bitwiseAnd(cirrusBitMask).eq(0));

  return img.divide(10000).updateMask(clear).set('system:time_start',img.get('system:time_start'))

def bandPassAdjustment(img):
  keep = img.select(['temp'])
  bands = ['blue','green','red','nir','swir1','swir2'];
  # linear regression coefficients for adjustment
  gain = ee.Array([[0.977], [1.005], [0.982], [1.001], [1.001], [0.996]]);
  bias = ee.Array([[-0.00411],[-0.00093],[0.00094],[-0.00029],[-0.00015],[-0.00097]]);
  # Make an Array Image, with a 2-D Array per pixel.
  arrayImage2D = img.select(bands).toArray().toArray(1);

  # apply correction factors and reproject array to geographic image
  componentsImage = ee.Image(gain).multiply(arrayImage2D).add(ee.Image(bias))\
    .arrayProject([0]).arrayFlatten([bands]).float();

  return keep.addBands(componentsImage)#.set('system:time_start',img.get('system:time_start'));

def filteredImageInCHIRPSToMapId(dateFrom=None, dateTo=None):
    """  """
    try:
        eeCollection = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")
        geometry = ee.Geometry.Point([5.2130126953125,15.358356179450585])
        colorPalette='ffffff,307b00,5a9700,86b400,b4cf00,e4f100,ffef00,ffc900,ffa200,ff7f00,ff5500'
        visParams={'opacity':1,'max':188.79177856445312,'palette':colorPalette}
        if (dateFrom and dateTo):
            eeFilterDate = ee.Filter.date(dateFrom, dateTo)
            eeCollection=eeCollection.filterBounds(geometry)
            eeCollection = eeCollection.filter(eeFilterDate)
        eeFirstImage = ee.Image(eeCollection.mean());
        values = imageToMapId(eeFirstImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def getTimeSeriesByCollectionAndIndex(collectionName, indexName, scale, coords=[], dateFrom=None, dateTo=None, reducer=None):
    """  """
    logger.error("************getTimeSeriesByCollectionAndIndex**********************")
    try:
        geometry = None
        indexCollection = None
        if isinstance(coords[0], list):
            geometry = ee.Geometry.Polygon(coords)
        else:
            geometry = ee.Geometry.Point(coords)
        if indexName != None:
            logger.error("collection: " + collectionName + " - indexName: " + indexName)
            indexCollection = ee.ImageCollection(collectionName).filterDate(dateFrom, dateTo).select(indexName)
        else:
            logger.error("indexName missing")
            indexCollection = ee.ImageCollection(collectionName).filterDate(dateFrom, dateTo)
        def getIndex(image):
            """  """
            logger.error("entered getImage")
            theReducer = None;
            if(reducer == 'min'):
                theReducer = ee.Reducer.min()
            elif (reducer == 'max'):
                theReducer = ee.Reducer.max()
            else:
                theReducer = ee.Reducer.mean()
            if indexName != None:
                logger.error("had indexName: " + indexName)
                indexValue = image.reduceRegion(theReducer, geometry, scale).get(indexName)
                logger.error("had indexName: " + indexName + " and indexValue is: " + indexValue)
            else:
                logger.error("noooooooooo indexName")
                indexValue = image.reduceRegion(theReducer, geometry, scale)
            date = image.get('system:time_start')
            indexImage = ee.Image().set('indexValue', [ee.Number(date), indexValue])
            return indexImage
        indexCollection1 = indexCollection.map(getIndex)
        indexCollection2 = indexCollection1.aggregate_array('indexValue')
        values = indexCollection2.getInfo()
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def aggRegion(regionList):
    """ helper function to take multiple values of region and aggregate to one value """
    values = []
    for i in range(len(regionList)):
        if i != 0:
            date = datetime.datetime.fromtimestamp(regionList[i][-2]/1000.).strftime("%Y-%m-%d")
            values.append([date,regionList[i][-1]])

    sort = sorted(values, key=lambda x: x[0])

    out = []
    for key, group in groupby(sort, key=lambda x: x[0][:10]):
        data = list(group)
        agg = sum(j for i, j in data if j != None)
        dates = key.split('-')
        timestamp = datetime.datetime(int(dates[0]),int(dates[1]),int(dates[2]))
        if agg != 0:
            out.append([int(timestamp.strftime('%s'))*1000,agg/float(len(data))])

    return out

def getTimeSeriesByIndex(indexName, scale, coords=[], dateFrom=None, dateTo=None, reducer=None):
    """  """
    try:
        geometry = None
        if isinstance(coords[0], list):
            geometry = ee.Geometry.Polygon(coords)
        else:
            geometry = ee.Geometry.Point(coords)
        if (indexName == 'NDVI'):
            indexCollection = filteredImageNDVIToMapId(dateFrom, dateTo,True)
        elif (indexName == 'EVI'):
            indexCollection = filteredImageEVIToMapId(dateFrom, dateTo,True)
        elif (indexName == 'EVI2'):
            indexCollection = filteredImageEVI2ToMapId(dateFrom, dateTo,True)
        elif (indexName == 'NDMI'):
            indexCollection = filteredImageNDMIToMapId(dateFrom, dateTo,True)
        elif (indexName == 'NDWI'):
            indexCollection = filteredImageNDWIToMapId(dateFrom, dateTo,True)

        values = indexCollection.getRegion(geometry, scale).getInfo()
        out = aggRegion(values)

    except EEException as e:
        try:
            getTimeSeriesByIndex(indexName, scale * 2, coords, dateFrom, dateTo, reducer);
        except EEException as e:
            raise GEEException(sys.exc_info()[0])
    return out

def getTimeSeriesByIndex2(indexName, scale, coords=[], dateFrom=None, dateTo=None):
    """  """
    bandsByCollection = {
        'LANDSAT/LC08/C01/T1_TOA': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
        'LANDSAT/LC08/C01/T2_TOA': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
        'LANDSAT/LE07/C01/T1_TOA': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7'],
        'LANDSAT/LE07/C01/T2_TOA': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7'],
        'LANDSAT/LT05/C01/T1_TOA': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7'],
        'LANDSAT/LT05/C01/T2_TOA': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7'],
        'LANDSAT/LT04/C01/T1_TOA': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7'],
        'LANDSAT/LT04/C01/T2_TOA': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']
    }
    indexes = {
        'NDVI': '(nir - red) / (nir + red)',
        'EVI': '2.5 * (nir - red) / (nir + 6.0 * red - 7.5 * blue + 1)',
        'EVI2': '2.5 * (nir - red) / (nir + 2.4 * red + 1)',
        'NDMI': '(nir - swir1) / (nir + swir1)',
        'NDWI': '(green - nir) / (green + nir)',
        'NBR': '(nir - swir2) / (nir + swir2)',
        'LSAVI': '((nir - red) / (nir + red + 0.5)) * (1 + 0.5)'
    }
    def create(name):
        """  """
        def maskClouds(image):
            """  """
            def isSet(types):
                """ https://landsat.usgs.gov/collectionqualityband """
                typeByValue = {
                    'badPixels': 15,
                    'cloud': 16,
                    'shadow': 256,
                    'snow': 1024,
                    'cirrus': 4096
                }
                anySet = ee.Image(0)
                for Type in types:
                    anySet = anySet.Or(image.select('BQA').bitwiseAnd(typeByValue[Type]).neq(0))
                return anySet
            return image.updateMask(isSet(['badPixels', 'cloud', 'shadow', 'cirrus']).Not())
        def toIndex(image):
            """  """
            bands = bandsByCollection[name]
            return image.expression(indexes[indexName], {
                'blue': image.select(bands[0]),
                'green': image.select(bands[1]),
                'red': image.select(bands[2]),
                'nir': image.select(bands[3]),
                'swir1': image.select(bands[4]),
                'swir2': image.select(bands[5]),
            }).clamp(-1, 1).rename(['index'])
        def toIndexWithTimeStart(image):
            """  """
            time = image.get('system:time_start')
            image = maskClouds(image)
            return toIndex(image).set('system:time_start', time)
        #
        if dateFrom and dateTo:
            return ee.ImageCollection(name).filterDate(dateFrom, dateTo).filterBounds(geometry).map(toIndexWithTimeStart, True)
        else:
            return ee.ImageCollection(name).filterBounds(geometry).map(toIndexWithTimeStart, True)
    def reduceRegion(image):
        """  """
        reduced = image.reduceRegion(ee.Reducer.median(), geometry=geometry, scale=scale, maxPixels=1e6)
        return ee.Feature(None, {
            'index': reduced.get('index'),
            'timeIndex': [image.get('system:time_start'), reduced.get('index')]
        })
    try:
        geometry = None
        if isinstance(coords[0], list):
            geometry = ee.Geometry.Polygon(coords)
        else:
            geometry = ee.Geometry.Point(coords)
        collection = ee.ImageCollection([])
        for name in bandsByCollection:
            collection = collection.merge(create(name))
        values = ee.ImageCollection(ee.ImageCollection(collection).sort('system:time_start').distinct('system:time_start'))\
            .map(reduceRegion)\
            .filterMetadata('index', 'not_equals', None)\
            .aggregate_array('timeIndex')
        values = values.getInfo()
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def getDegradationPlotsByPoint(geometry, start, end):
    logger.error("Entered getDegradationPlotsByPoint")
    logger.error("going to get LANDSAT")
    allLandsat = gee.inputs.getLandsat({
        "start": start,
        "end": end,
        "targetBands": ['SWIR1','NIR','RED','GREEN','BLUE','SWIR2','NDFI']
    })
    logger.error("got LANDSAT")
    if isinstance(geometry[0], list):
        logger.error("making polygon")
        geometry = ee.Geometry.Polygon(geometry)
    else:
        logger.error("making point")
        geometry = ee.Geometry.Point(geometry)
    landsatData = allLandsat.filterBounds(geometry)
    logger.error("filtered bounds")
    return getImagePlot(landsatData,geometry, geometry, 'NDFI', 4)

def getImagePlot(iCol, region, point, bandName, position):
    # Make time series plot from image collection
    logger.error("entered getImagePlot")
    def toValue(image):
        logger.error("entered toValue")
        image = ee.Image(image)
        image_date = ee.Date(image.date())
        logger.error("image_date: " + image_date)
        year = image_date.get('year')
        doy = image_date.getRelative('day', 'year')
        return (ee.Feature(None, image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=30
        )).set('date', image_date)
                .set('image_year', year)
                .set('image_julday', doy)
                )

    return ee.ImageCollection(iCol).select(bandName)\
        .filterBounds(region) \
        .map(toValue) \
        .sort('date') \
        .get('list') \
        .getInfo()
        #, ee.Reducer.mean(), 30

def getTimeSeriesForPoint(point, dateFrom=None, dateTo=datetime.datetime.now()):
    """ https://code.earthengine.google.com/49592558df4df130e9082f94a23a887f """

    bandNames = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'temp', 'pixel_qa']
    #TODO: implement image_year and image_julday on the client side. Keep it for now for TimeSync
    properties = bandNames + ['date', 'image_year', 'image_julday']

    def toValue(image):
        image = ee.Image(image)
        image_date = ee.Date(image.date())
        year = image_date.get('year')
        doy = image_date.getRelative('day', 'year')
        return (ee.Feature(None, image.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=1
        )).set('date', image_date)
         .set('image_year', year)
         .set('image_julday', doy)
        )

    def mask(image):
        image = ee.Image(image)
        def isOneOf(types):
            typeByValue = {'water': 4, 'shadow': 8, 'snow': 16, 'cloud': 32}
            return reduce((lambda acc, Type: acc.Or(image.select(['pixel_qa']).bitwiseAnd(typeByValue[Type]).neq(0))), types, ee.Image(0))
        return image.updateMask(isOneOf(['shadow', 'cloud']).Not())

    def listToObject(values):
        obj = dict()
        for i, value in enumerate(values):
            obj[properties[i]] = value
        return obj

    collectionBands = [{
        'name': 'LANDSAT/LC08/C01/T1_SR',
        'bands': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'pixel_qa']
    }, {
        'name': 'LANDSAT/LE07/C01/T1_SR',
        'bands': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B6', 'pixel_qa']
    }, {
        'name': 'LANDSAT/LT05/C01/T1_SR',
        'bands': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B6', 'pixel_qa']
    }, {
        'name': 'LANDSAT/LT04/C01/T1_SR',
        'bands': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B6', 'pixel_qa']
    }]

    collectionBands = map(lambda collectionDef: ee.ImageCollection(collectionDef['name']).select(collectionDef['bands'], bandNames), collectionBands)
    collectionBands = reduce((lambda acc, c: acc.merge(c)), collectionBands)
    collectionBands = collectionBands.filterBounds(point)
    if dateFrom:
        collectionBands = collectionBands.filterDate(dateFrom, dateTo)
    collectionBands = collectionBands.map(mask)\
        .map(toValue)\
        .sort('date')\
        .reduceColumns(ee.Reducer.toList(len(properties)), properties)\
        .get('list')\
        .getInfo()
    collectionBands = map(listToObject, collectionBands)

    return collectionBands

def getTimeSeriesAssetForPoint(point, dateFrom=None, dateTo=datetime.datetime.now()):
    def sampleUsingPoint(image):
        image = ee.Image(image)
        timestamp = image.get("system:time_start")
        sampledValue = image.sample(ee.Geometry.Point(point),30).first().get(image.bandNames().get(0));
        return [timestamp, sampledValue]

    def toDict(array):
        d = {}
        for pair in array:
            d[pair[0]] = pair[1]
        return d
    try:
        tcc = ee.ImageCollection("projects/servir-mekong/UMD/tree_canopy")
        tcc = toDict(tcc.toList(tcc.size()).map(sampleUsingPoint).getInfo())
        loss = ee.ImageCollection("projects/servir-mekong/UMD/loss")
        loss = toDict(loss.toList(loss.size()).map(sampleUsingPoint).getInfo())
        croplands = ee.ImageCollection("projects/servir-mekong/yearly_primitives_smoothed/cropland")
        croplands = toDict(croplands.toList(croplands.size()).map(sampleUsingPoint).getInfo())
        # alltimestamps = reduce(lambda x, y: x.union(y.keys()), [tcc,loss,croplands], set())
        alltimestamps = list(set().union(tcc.keys(),loss.keys(),croplands.keys()))
        alltimestamps.sort()
        timeseries = []
        for timestamp in alltimestamps:
            tempdict = {}
            if (timestamp in tcc):
                tempdict["tcc"] = tcc[timestamp]
            else:
                tempdict["tcc"] = None
            if (timestamp in loss):
                tempdict["loss"] = loss[timestamp]
            else:
                tempdict["loss"] = None
            if (timestamp in croplands):
                tempdict["croplands"] = croplands[timestamp]
            else:
                tempdict["croplands"] = None
            timeseries.append([timestamp, tempdict])
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return timeseries

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

def getAsterMosaic(visParams={}, dateFrom=None, dateTo=None):
    """  """
    try:
        def normalize(image):
            """  """
            bands = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B10']
            coefficients = [ee.Image(ee.Number(image.get('GAIN_COEFFICIENT_' + band))).float().rename([band]) for band in bands]
            coefficients = ee.Image.cat(coefficients)
            cloudCover = ee.Image(ee.Number(image.get('CLOUDCOVER'))).float().multiply(-1).add(100).rename(['cloudCover'])
            image = image.select(bands).subtract(1).multiply(coefficients)
            image = image.select(bands, ['green', 'red', 'nir', 'swir1', 'swir2', 'thermal'])
            return image.addBands(cloudCover)
        collection = ee.ImageCollection('ASTER/AST_L1T_003') \
            .filterDate(dateFrom, dateTo) \
            .filter(ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B01')) \
            .filter(ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B02')) \
            .filter(ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B3N')) \
            .filter(ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B04')) \
            .filter(ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B05')) \
            .filter(ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B10')) \
            .map(normalize)
        mosaic = collection.qualityMosaic('cloudCover')
        #visParams = {'bands': 'nir, swir1, red', 'min': 0, 'max': '110, 25, 90', 'gamma': 1.7}
        values = imageToMapId(mosaic, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def getNdviChange(visParams={}, yearFrom=None, yearTo=None):
    """  """
    try:
        def map1(image):
            """  """
            return addBands(image, ee.List(['B4', 'B8A', 'B11'])).updateMask(image.select('QA60').lt(1024))
        def map2(image):
            """  """
            return addBands(image, ee.List(['B4', 'B5', 'B6'])).updateMask(landsatCollection1Mask(image))
        def map3(image):
            """  """
            return addBands(image, ee.List(['B3', 'B4', 'B5'])).updateMask(landsatCollection1Mask(image))
        def maxNdvi(year):
            """  """
            from1 = ee.Date.fromYMD(int(year), 1, 1)
            to = ee.Date.fromYMD(int(year) + 1, 1, 1)
            s2 = ee.ImageCollection('COPERNICUS/S2').filterDate(from1, to).map(map1)
            l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA').filterDate(from1, to).map(map2)
            l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA').filterDate(from1, to).map(map3)
            l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_TOA').filterDate(from1, to).map(map3)
            return ee.ImageCollection(s2.merge(l8).merge(l7).merge(l5)).max()
        def addBands(image, bands):
            """  """
            return image.select(bands, ['red', 'nir', 'swir1']).normalizedDifference(['nir', 'red']).rename(['ndvi'])
        def landsatCollection1Mask(image):
            """  """
            def is_set(types):
                """  """
                typeByValue = {'badPixels': 15, 'cloud': 16, 'shadow': 256, 'snow': 1024, 'cirrus': 4096}
                any_set = ee.Image(0)
                for type in types:
                    any_set = any_set.Or(image.select('BQA').bitwiseAnd(typeByValue[type]).neq(0))
                return any_set
            return is_set(['badPixels', 'cloud', 'shadow', 'cirrus']).Not()
        def change(year1, year2):
            """  """
            ndvi1 = maxNdvi(year1)
            ndvi2 = maxNdvi(year2)
            change = ndvi2.select('ndvi').subtract(ndvi1.select('ndvi')) \
                .updateMask(ee.Image('MODIS/MOD44W/MOD44W_005_2000_02_24').select('water_mask').Not())
            return change
        values = imageToMapId(change(yearFrom, yearTo), visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredImageCompositeToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None, metadataCloudCoverMax=90, simpleCompositeVariable=60):
    """  """
    try:
        logger.error('******filteredImageCompositeToMapId************')
        eeCollection = ee.ImageCollection(collectionName)
        logger.error('******eeCollection ************')
        if (dateFrom and dateTo):
            eeFilterDate = ee.Filter.date(dateFrom, dateTo)
            eeCollection = eeCollection.filter(eeFilterDate).filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
        eeMosaicImage = ee.Algorithms.Landsat.simpleComposite(eeCollection, simpleCompositeVariable, 10, 40, True)
        logger.error('******eeMosaicImage************')
        values = imageToMapId(eeMosaicImage, visParams)
    except EEException as e:
        raise GEEException(sys.exc_info()[0])
    return values

def filteredSentinelComposite(visParams={}, dateFrom=None, dateTo=None, metadataCloudCoverMax=10):
    def cloudScore(img):
        def rescale(img, exp, thresholds):
            return img.expression(exp, {'img': img}).subtract(thresholds[0]).divide(thresholds[1] - thresholds[0])
        score = ee.Image(1.0)
        score = score.min(rescale(img, 'img.B2', [0.1, 0.3]))
        score = score.min(rescale(img, 'img.B4 + img.B3 + img.B2', [0.2, 0.8]))
        score = score.min(rescale(img, 'img.B8 + img.B11 + img.B12', [0.3, 0.8]))
        ndsi = img.normalizedDifference(['B3', 'B11'])
        return score.min(rescale(ndsi, 'img', [0.8, 0.6]))
    def cloudScoreS2(img):
        rescale = img.divide(10000)
        score = cloudScore(rescale).multiply(100).rename('cloudscore')
        return img.addBands(score)
    sentinel2 = ee.ImageCollection('COPERNICUS/S2')
    f2017s2 = sentinel2.filterDate(dateFrom, dateTo).filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', metadataCloudCoverMax)
    m2017s2 = f2017s2.map(cloudScoreS2)
    m2017s3 = m2017s2.median()
    return imageToMapId(m2017s3, visParams)

def listAvailableBands(name, isImage):
    eeImage = None
    if isImage == True:
        eeImage = ee.Image(name)
    else:
        eeImage = ee.ImageCollection(name).first()
    return {
        'bands': eeImage.bandNames().getInfo(),
        'imageName' : name
    }


########################## TimeSync Related Functions ##########################

#due to saturation, bruce updated the stretch parameters to
VIS_743 = {"bands": ["B7", "B4", "B3"], "min": [-904, 151, -300], "max": [3696, 4951, 2500]}
VIS_432 = {"bands": ["B4", "B3", "B2"], "min": [151, -300, 50], "max": [4951, 2500, 1150]}
VIS_543 = {"bands": ["B5", "B4", "B3"], "min": [-804, 151, -300], "max": [3800, 4951, 2500]}
VIS_BGW = {"bands": ["B", "G", "W"], "min": [604, 49, -2245], "max": [5592, 3147, 843]}

VIS_SET = {'tc': VIS_BGW, 'b743': VIS_743, 'b432': VIS_432, 'b543': VIS_543}

BAND_NAMES = ["B1", "B2", "B3", "B4", "B5", "B7", 'cfmask']
BAND_SET = {'LT04': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
            'LT05': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
            'LE07': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
            'LC08': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa']}

def tcTransform(image):
    b = ee.Image(image).select(["B1", "B2", "B3", "B4", "B5", "B7"])
    brt_coeffs = ee.Image([0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303])
    grn_coeffs = ee.Image([-0.1603, -0.2819, -0.4934, 0.7940, -0.0002, -0.1446])
    wet_coeffs = ee.Image([0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109])

    sum = ee.call("Reducer.sum")
    brightness = b.multiply(brt_coeffs).reduce(sum)
    greenness = b.multiply(grn_coeffs).reduce(sum)
    wetness = b.multiply(wet_coeffs).reduce(sum)

    return ee.Image(brightness).addBands(greenness).addBands(wetness).select([0,1,2], ['B','G','W'])

def parseQA2FMask(image):
    qa = ee.Image(image).select(['cfmask'])
    cloud = qa.bitwiseAnd(32)
    snow = qa.bitwiseAnd(16)
    shadow = qa.bitwiseAnd(8)
    water = qa.bitwiseAnd(4)
    clear = qa.bitwiseAnd(2)

    #cfmask:    {0: clear, 1: water, 2: shadow, 3: snow, 4: cloud}
    #modified fmask: {0: clear, 1: water, 3: shadow, 2: snow, 4: cloud}
    cfmask = (clear.eq(0)
              .where(water.gt(0), 1)
              .where(snow.gt(0), 2)
              .where(shadow.gt(0), 3)
              .where(cloud.gt(0), 4)
              .rename('cfmask'))

    return ee.Image(image).select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7']) \
        .addBands(cfmask) \
        .set('YYYYDDD', ee.Date(image.get('system:time_start')).format('YYYYDDD'))

def getImageCollection(point, year=None):
    '''
    Get collection 1 images
    :param point:
    :return:
    '''
    aoi = ee.Geometry.Point(point)

    lc8_collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterBounds(aoi).select(BAND_SET['LC08'], BAND_NAMES)
    le7_collection = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filterBounds(aoi).select(BAND_SET['LE07'], BAND_NAMES)
    lt5_collection = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').filterBounds(aoi).select(BAND_SET['LT05'], BAND_NAMES)
    lt4_collection = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR').filterBounds(aoi).select(BAND_SET['LT04'], BAND_NAMES)

    all = (lt4_collection.merge(lt5_collection)
           .merge(le7_collection)
           .merge(lc8_collection)
           .map(parseQA2FMask)
           .map(lambda image: image.set('YYYYDDD', ee.Date(image.get('system:time_start')).format('YYYYDDD')))
           .distinct('YYYYDDD')
           .sort('system:time_start'))

    if year:
        d1 = ee.Date.fromYMD(year, 1, 1)
        d2 = ee.Date.fromYMD(year, 12, 31)
        all = all.filterDate(d1, d2)

    return all

def getLandsatImages(point, year=None):
    all = getImageCollection(point, year)
    ids = all.toList(all.size()).map(lambda image: ee.Image(image).get('system:id'))
    return ids.getInfo()

def createChip(image, point, vis, size=255):
    '''
    generate a chip for an image
    '''
    this_image = ee.Image(image)
    iid = this_image.get('system:id').getInfo()
    doy = ee.Date(this_image.get('system:time_start')).getRelative('day', 'year').getInfo()
    sensor = this_image.get('SATELLITE').getInfo()
    src_bands = BAND_SET['LT05']
    if sensor == 'LANDSAT_8':
        src_bands = BAND_SET['LC08']

    pixelSize = ee.Image(image).projection().nominalScale()
    box = ee.Geometry.Point(point).buffer(pixelSize.multiply(size / 2.0), 5).bounds(5)

    image = this_image.select(src_bands, BAND_NAMES)
    if vis == 'tc':
        image = tcTransform(image)

    params = {'dimensions': '%dx%d' % (size, size),
              'region': box.getInfo()['coordinates'],
              'format': 'png'}

    chip_url = ee.Image(image).visualize(**VIS_SET[vis]).unmask().getThumbURL(params)

    return {"iid": iid, "doy": doy, "chip_url": chip_url}

def createChipXYZ(image, point, vis, size=255):
    '''
    generate a chip for an image
    '''
    this_image = ee.Image(image)
    iid = this_image.get('system:id').getInfo()
    doy = ee.Date(this_image.get('system:time_start')).getRelative('day', 'year').getInfo()
    sensor = this_image.get('SATELLITE').getInfo()
    src_bands = BAND_SET['LT05']
    if sensor == 'LANDSAT_8':
        src_bands = BAND_SET['LC08']

    pixelSize = ee.Image(image).projection().nominalScale()
    box = ee.Geometry.Point(point).buffer(pixelSize.multiply(size / 2.0), 5).bounds(5)

    image = this_image.select(src_bands, BAND_NAMES)
    if vis == 'tc':
        image = tcTransform(image)

    mapid = ee.Image(image).clip(box).unmask().visualize(**VIS_SET[vis]).getMapId()
    
    chip_url = 'https://earthengine.googleapis.com/map/%s/{z}/{x}/{y}?token=%s' % (mapid['mapid'], mapid['token'])

    return {"iid": iid, "doy": doy, "chip_url": chip_url}

def qaTargetDay(point, day):
    def qa(img):
        #cfmask:    {0: clear, 1: water, 2: shadow, 3: snow, 4: cloud}
        #modified fmask: {0: clear, 1: water, 3: shadow, 2: snow, 4: cloud, 9: nodata}
        cfmask = ee.Image(img).select(['cfmask']).unmask(9) \
            .reduceRegion(reducer=ee.Reducer.first(),
                          geometry=ee.Geometry.Point(point),
                          scale=30,
                          tileScale=16) \
            .get('cfmask')
        offset = ee.Number(cfmask).multiply(1000).add(img.date().getRelative('day', 'year').subtract(day).abs())
        return img.set('offset', offset)
    return qa

def getLandsatChipForYearByTargetDay(point, year, day, vis):

    images = ee.ImageCollection(getImageCollection(point, year))
    image = images.map(qaTargetDay(point, day)).sort('offset').first()
    # image = images.map(lambda img: img.set('offset', (ee.Date(img.get('system:time_start'))
    #                                                         .getRelative('day', 'year')
    #                                                         .subtract(day)
    #                                                         .abs()))).sort('offset').first()

    chip = None
    if image:
        chip = createChip(image, point, vis)

    return chip


def getSpectralsForPoint(collection, point):
    """ https://code.earthengine.google.com/49592558df4df130e9082f94a23a887f """

    # bandNames = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask']
    bandNames = ["B1", "B2", "B3", "B4", "B5", "B7", 'cfmask']
    #TODO: implement image_year and image_julday on the client side. Keep it for now for TimeSync
    properties = bandNames + ['image_year', 'image_julday', 'iid']

    def toValue(image):
        image = ee.Image(image)
        image_date = ee.Date(image.date())
        year = image_date.get('year')
        doy = image_date.getRelative('day', 'year')

        #TODO: should rescaling be applied when collection is made?
        scaled = image.select(["B1", "B2", "B3", "B4", "B5", "B7"]).divide(10000).addBands(image.select(['cfmask']))

        return (ee.Feature(None, scaled.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=30,
            tileScale=16
        )).set('image_year', year)
                .set('image_julday', doy)
                .set('iid', image.get('system:id'))
                )

    def listToObject(values):
        obj = dict()
        for i, value in enumerate(values):
            obj[properties[i]] = value
        return obj

    collectionBands = collection.map(toValue) \
        .reduceColumns(ee.Reducer.toList(len(properties)), properties) \
        .get('list') \
        .getInfo()

    collectionBands = list(map(listToObject, collectionBands))

    return collectionBands


def getTsTimeSeriesForPoint(point):
    collection = ee.ImageCollection(getImageCollection(point))#.map(parseQA2FMask)
    return getSpectralsForPoint(collection, ee.Geometry.Point(point))
    # return getTimeSeriesForPoint(ee.Geometry.Point(point))

def getTsTimeSeriesForPointByYear(point, year):
    collection = ee.ImageCollection(getImageCollection(point)) \
        .filterDate(ee.Date.fromYMD(year, 1, 1), ee.Date.fromYMD(year, 12, 31)) \
        .map(parseQA2FMask)

    return getSpectralsForPoint(collection, ee.Geometry.Point(point))
    # return getTimeSeriesForPoint(ee.Geometry.Point(point))

def getTsTimeSeriesForPointByTargetDay(point, day, startYear=1985, endYear=None):
    '''
        retrieve time series for specified year range using target day.
    '''
    #by default assume the end year is the year before current date.
    if endYear == None:
        endYear = datetime.date.today().year - 1

    # collection = (ee.ImageCollection(getImageCollection(point))
    #                     # .map(parseQA2FMask)
    #                     .map(lambda img: img.set('offset', (img.date().getRelative('day', 'year')
    #                                                         .subtract(day)
    #                                                         .abs())))
    # )

    collection = (ee.ImageCollection(getImageCollection(point))
                  .map(qaTargetDay(point, day))
                  )

    images = ee.List.sequence(startYear, endYear).map(
        lambda y: collection.filterDate(ee.Date.fromYMD(y, 1, 1), ee.Date.fromYMD(y, 12, 31)).sort('offset').first()
    )

    return getSpectralsForPoint(ee.ImageCollection(images), ee.Geometry.Point(point))
    # return getTimeSeriesForPoint(ee.Geometry.Point(point))
