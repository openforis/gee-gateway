import ee
from ee.ee_exception import EEException

from gee_exception import GEEException

def initialize(ee_account='', ee_key_path=''):
    try:
        ee.Initialize()
    except EEException:
        from oauth2client.service_account import ServiceAccountCredentials
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            service_account_email=ee_account,
            filename=ee_key_path,
            private_key_password='notasecret',
            scopes=ee.oauth.SCOPE + ' https://www.googleapis.com/auth/drive ')
        ee.Initialize(credentials)

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

def meanImageInMosaicToMapId(collectionName, visParams={}, dateFrom=None, dateTo=None):
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

def filteredImageByIndexToMapId(iniDate=None, endDate=None, index='ndvi'):
    """  """
    try:
        if (index == 'ndvi'):
            values = filteredImageNDVIToMapId(iniDate, endDate)
        elif (index == 'evi'):
            values = filteredImageEVIToMapId(iniDate, endDate)
        elif (index == 'evi2'):
            values = filteredImageEVI2ToMapId(iniDate, endDate)
        elif (index == 'ndmi'):
            values = filteredImageNDMIToMapId(iniDate, endDate)
        elif (index == 'ndwi'):
            values = filteredImageNDWIToMapId(iniDate, endDate)
    except EEException as e:
        raise GEEException(e.message)
    return values

def filteredImageNDVIToMapId(iniDate=None, endDate=None):
    """  """
    def calcNDVI(img):
        return img.expression('(i.nir - i.red) / (i.nir + i.red)',  {'i': img)
    try:
        eeCollection = getLandSatMergedCollection() #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='c9c0bf,435ebf,eee8aa,006400'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        ndviImage = ee.Image(eeCollection.map(calcNDVI).mean())
        values = imageToMapId(ndviImage, visParams)
    except EEException as e:
        raise GEEException(e.message)
    return values

def filteredImageEVIToMapId(iniDate=None, endDate=None):
    """  """
    def calcEVI(img):
        return img.expression('2.5 * (i.nir - i.red) / (i.nir + 6.0 * i.red - 7.5 * i.blue + 1)',  {'i': img})
    try:
        eeCollection = getLandSatMergedCollection() #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='F5F5F5,E6D3C5,C48472,B9CF63,94BF3D,6BB037,42A333,00942C,008729,007824,004A16'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        eviImage = ee.Image(eeCollection.map(calcEVI).mean())
        values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(e.message)
    return values

def filteredImageEVI2ToMapId(iniDate=None, endDate=None):
    """  """
    def calcEVI2(img):
        return img..expression('2.5 * (i.nir - i.red) / (i.nir + 2.4 * i.red + 1)',  {'i': img})
    try:
        eeCollection = getLandSatMergedCollection() #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='F5F5F5,E6D3C5,C48472,B9CF63,94BF3D,6BB037,42A333,00942C,008729,007824,004A16'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        eviImage = ee.Image(eeCollection.map(calcEVI2).mean())
        values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(e.message)
    return values

def filteredImageNDMIToMapId(iniDate=None, endDate=None):
    """  """
    def calcNDMI(img):
        return img.expression('(i.nir - i.swir1) / (i.nir + i.swir1)',  {'i': img})
    try:
        eeCollection = getLandSatMergedCollection() #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='0000FE,2E60FD,31B0FD,00FEFE,50FE00,DBFE66,FEFE00,FFBB00,FF6F00,FE0000'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        eviImage = ee.Image(eeCollection.map(calcNDMI).mean())
        values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(e.message)
    return values

def filteredImageNDWIToMapId(iniDate=None, endDate=None):
    """  """
    def calcNDWI(img):
        return img.expression('(i.green - i.nir) / (i.green + i.nir)',  {'i': img)
    try:
        eeCollection = getLandSatMergedCollection() #ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))
        colorPalette='505050,E8E8E8,00FF33,003300'
        visParams={'opacity':1,'max':1, 'min' : -1,'palette':colorPalette}
        eviImage = ee.Image(eeCollection.map(calcNDWI).mean())
        values = imageToMapId(eviImage, visParams)
    except EEException as e:
        raise GEEException(e.message)
    return values

def getLandSatMergedCollection():
    eeCollection = None
    try:
        sensorBandDictLandsatTOA = {'L8': [1,2,3,4,5,9,6],
                                    'L7': [0,1,2,3,4,5,7],
                                    'L5': [0,1,2,3,4,5,6],
                                    'L4': [0,1,2,3,4,5,6]}
        bandNamesLandsatTOA = ['blue','green','red','nir','swir1','temp','swir2']
        metadataCloudCoverMax = 100
        #region = ee.Geometry.Point([5.2130126953125,15.358356179450585])
        #.filterBounds(region).filterDate(iniDate,endDate)\
        lt4 = ee.ImageCollection('LANDSAT/LT4_L1T_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L4'],bandNamesLandsatTOA)
        lt5 = ee.ImageCollection('LANDSAT/LT5_L1T_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L5'],bandNamesLandsatTOA)
        le7 = ee.ImageCollection('LANDSAT/LE7_L1T_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L7'],bandNamesLandsatTOA)
        lc8 = ee.ImageCollection('LANDSAT/LC8_L1T_TOA')\
            .filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)\
            .select(sensorBandDictLandsatTOA['L8'],bandNamesLandsatTOA)
        eeCollection = ee.ImageCollection(lt4.merge(lt5).merge(le7).merge(lc8))\
                        .map(maskClouds)
    except EEException as e:
        raise GEEException(e.message)
    return eeCollection

def maskClouds(self,img,cloudThresh=10):
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
        raise GEEException(e.message)
    return values

def getTimeSeriesByCollectionAndIndex(collectionName, indexName, scale, coords=[], dateFrom=None, dateTo=None, reducer=None):
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
            theReducer = None;
            if(reducer == 'min'):
                theReducer = ee.Reducer.min()
            elif (reducer == 'max'):
                theReducer = ee.Reducer.max()
            else:
                theReducer = ee.Reducer.mean()
            indexValue = image.reduceRegion(theReducer, geometry, scale).get(indexName)
            date = image.get('system:time_start')
            indexImage = ee.Image().set('indexValue', [ee.Number(date), indexValue])
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
            'NDMI': '(i.nir - i.swir1) / (i.nir + i.swir1)',
            'NDWI': '(i.green - i.nir) / (i.green + i.nir)'
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
            return ee.Algorithms.If(cfmask, ee.Algorithms.If(ee.Number(cfmask).eq(1), ee.List([time, index]), None), None)
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
        raise GEEException(e.message)
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
        def map4(image):
            """  """
            return addBands(image, ee.List(['B3', 'B4', 'B5'])).updateMask(image.select('fmask').lt(2))
        def maxNdvi(year):
            """  """
            from1 = ee.Date.fromYMD(int(year), 1, 1)
            to = ee.Date.fromYMD(int(year) + 1, 1, 1)
            s2 = ee.ImageCollection('COPERNICUS/S2').filterDate(from1, to).map(map1)
            l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA').filterDate(from1, to).map(map2)
            l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA').filterDate(from1, to).map(map3)
            l5 = ee.ImageCollection('LANDSAT/LT5_L1T_TOA_FMASK').filterDate(from1, to).map(map4)
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
        raise GEEException(e.message)
    return values
