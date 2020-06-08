# GitHub URL: https://github.com/giswqs/qgis-earthengine-examples/tree/master/inputs.py

import ee
import gee.dates as dateUtils
import gee.ccdc as ccdcUtils

import logging
import logging.config
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
handler = RotatingFileHandler('gee-gateway-nginx.log', maxBytes=10485760, backupCount=10)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


##################################
#
# Utility functions for getting inputs for CCDC
#
################################/*/

def getLandsat(options):
    logger.error("going to get LANDSAT")
    if options is None:
        return ("Error")
    else:
        logger.error("got options")
        if 'start' in options:
            logger.error("start exists")
            start = options['start']
        else:
            start = '1990-01-01'
        if 'end' in options:
            end = options['end']
        else:
            end = '2021-01-01'
        if 'startDOY' in options:
            startDOY = options['startDOY']
        else:
            startDOY = 1
        if 'endDOY' in options:
            endDOY = options['endDOY']
        else:
            endDOY = 366
        if 'region' in options:
            region = options['region']
        else:
            region = None
        if 'targetBands' in options:
            targetBands = options['targetBands']
        else:
            targetBands = ['BLUE','GREEN','RED','NIR','SWIR1','SWIR2','NBR','NDFI','NDVI','GV','NPV','Shade','Soil']
        if 'useMask' in options:
            useMask = options['useMask']
        else:
            useMask = True
        if 'sensors' in options:
            sensors = options['sensors']
        else:
            sensors = {"l4": True, "l5": True, "l7": True, "l8": True}
        if useMask == 'No':
            useMask = False
        logger.error("all options set")
        logger.error("start, end" + start + ", " + end)
        # Filter using new filtering functions
        col = None
        fcollection4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR').filterDate(start, end).filterBounds(region)
        f4size = fcollection4.size().getInfo()
        if f4size > 0:
            collection4 = fcollection4.map(prepareL4L5, True).sort('system:time_start')
            col = collection4
        fcollection5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').filterDate(start, end).filterBounds(region)
        f5size = fcollection5.size().getInfo()
        if f5size > 0:
            logger.error("inside f5size")
            collection5 = fcollection5.map(prepareL4L5, True).sort('system:time_start')
            if col is None:
                col = collection5
            else:
                col = col.merge(collection5)
        fcollection7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filterDate(start, end).filterBounds(region)
        f7size = fcollection7.size().getInfo()
        if f7size > 0:
            collection7 = fcollection7.map(prepareL7, True).sort('system:time_start')
            if col is None:
                col = collection7
            else:
                col = col.merge(collection7)
        fcollection8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterDate(start, end).filterBounds(region)
        f8size = fcollection8.size().getInfo()
        if fcollection8.size().getInfo() > 0:
            collection8 = fcollection8.map(prepareL8, True).sort('system:time_start')
            if col is None:
                col = collection8
            else:
                col = col.merge(collection8)

        if region is not None:
            col = col.filterBounds(region)
        indices = doIndices(col).select(targetBands)
        if "l5" not in sensors:
            indices = indices.filterMetadata('SATELLITE','not_equals','LANDSAT_5')
        if "l4" not in sensors:
            indices = indices.filterMetadata('SATELLITE','not_equals','LANDSAT_4')
        if "l7" not in sensors:
            indices = indices.filterMetadata('SATELLITE','not_equals','LANDSAT_7')
        if "l8" not in sensors:
            indices = indices.filterMetadata('SATELLITE','not_equals','LANDSAT_8')
        indices = indices.filter(ee.Filter.dayOfYear(startDOY, endDOY))
    return ee.ImageCollection(indices)

def doIndices(collection):
    def indicesMapper(image):
        NDVI =  calcNDVI(image)
        NBR = calcNBR(image)
        EVI = calcEVI(image)
        EVI2 = calcEVI2(image)
        TC = tcTrans(image)
        # NDFI function requires surface reflectance bands only
        BANDS = ['BLUE','GREEN','RED','NIR','SWIR1','SWIR2']
        NDFI = calcNDFI(image.select(BANDS))
        return image.addBands([NDVI, NBR, EVI, EVI2, TC, NDFI])
    return collection.map(indicesMapper)

def calcNDVI(image):
   ndvi = ee.Image(image).normalizedDifference(['NIR', 'RED']).rename('NDVI')
   return ndvi

def calcNBR(image):
  nbr = ee.Image(image).normalizedDifference(['NIR', 'SWIR2']).rename('NBR')
  return nbr

def calcNDFI(image):
  gv = [.0500, .0900, .0400, .6100, .3000, .1000]
  shade = [0, 0, 0, 0, 0, 0]
  npv = [.1400, .1700, .2200, .3000, .5500, .3000]
  soil = [.2000, .3000, .3400, .5800, .6000, .5800]
  cloud = [.9000, .9600, .8000, .7800, .7200, .6500]
  cf = .1 # Not parameterized
  cfThreshold = ee.Image.constant(cf)
  unmixImage = ee.Image(image).unmix([gv, shade, npv, soil, cloud], True,True) \
                  .rename(['band_0', 'band_1', 'band_2','band_3','band_4'])
  newImage = ee.Image(image).addBands(unmixImage)
  mask = newImage.select('band_4').lt(cfThreshold)
  ndfi = ee.Image(unmixImage).expression(
    '((GV / (1 - SHADE)) - (NPV + SOIL)) / ((GV / (1 - SHADE)) + NPV + SOIL)', {
      'GV': ee.Image(unmixImage).select('band_0'),
      'SHADE': ee.Image(unmixImage).select('band_1'),
      'NPV': ee.Image(unmixImage).select('band_2'),
      'SOIL': ee.Image(unmixImage).select('band_3')
    })

  return ee.Image(newImage) \
        .addBands(ee.Image(ndfi).rename(['NDFI'])) \
        .select(['band_0','band_1','band_2','band_3','NDFI']) \
        .rename(['GV','Shade','NPV','Soil','NDFI']) \
        .updateMask(mask)


def calcEVI(image):

  evi = ee.Image(image).expression(
          'float(2.5*(((B4) - (B3)) / ((B4) + (6 * (B3)) - (7.5 * (B1)) + 1)))',
          {
              'B4': ee.Image(image).select(['NIR']),
              'B3': ee.Image(image).select(['RED']),
              'B1': ee.Image(image).select(['BLUE'])
          }).rename('EVI')

  return evi

def calcEVI2(image):
  evi2 = ee.Image(image).expression(
        'float(2.5*(((B4) - (B3)) / ((B4) + (2.4 * (B3)) + 1)))',
        {
            'B4': image.select('NIR'),
            'B3': image.select('RED')
        })
  return evi2

def tcTrans(image):

    # Calculate tasseled cap transformation
    brightness = image.expression(
        '(L1 * B1) + (L2 * B2) + (L3 * B3) + (L4 * B4) + (L5 * B5) + (L6 * B6)',
        {
            'L1': image.select('BLUE'),
            'B1': 0.2043,
            'L2': image.select('GREEN'),
            'B2': 0.4158,
            'L3': image.select('RED'),
            'B3': 0.5524,
            'L4': image.select('NIR'),
            'B4': 0.5741,
            'L5': image.select('SWIR1'),
            'B5': 0.3124,
            'L6': image.select('SWIR2'),
            'B6': 0.2303
        })
    greenness = image.expression(
        '(L1 * B1) + (L2 * B2) + (L3 * B3) + (L4 * B4) + (L5 * B5) + (L6 * B6)',
        {
            'L1': image.select('BLUE'),
            'B1': -0.1603,
            'L2': image.select('GREEN'),
            'B2': -0.2819,
            'L3': image.select('RED'),
            'B3': -0.4934,
            'L4': image.select('NIR'),
            'B4': 0.7940,
            'L5': image.select('SWIR1'),
            'B5': -0.0002,
            'L6': image.select('SWIR2'),
            'B6': -0.1446
        })
    wetness = image.expression(
        '(L1 * B1) + (L2 * B2) + (L3 * B3) + (L4 * B4) + (L5 * B5) + (L6 * B6)',
        {
            'L1': image.select('BLUE'),
            'B1': 0.0315,
            'L2': image.select('GREEN'),
            'B2': 0.2021,
            'L3': image.select('RED'),
            'B3': 0.3102,
            'L4': image.select('NIR'),
            'B4': 0.1594,
            'L5': image.select('SWIR1'),
            'B5': -0.6806,
            'L6': image.select('SWIR2'),
            'B6': -0.6109
        })

    bright =  ee.Image(brightness).rename('BRIGHTNESS')
    green = ee.Image(greenness).rename('GREENNESS')
    wet = ee.Image(wetness).rename('WETNESS')

    tasseledCap = ee.Image([bright, green, wet])
    return tasseledCap

def makeLatGrid(minY, maxY, minX, maxX, size):

    ySeq = ee.List.sequence(minY, maxY, size)
    numFeats = ySeq.length().subtract(2)
    def latGridMapper(num):
        num = ee.Number(num)
        num2 = num.add(1)
        y1 = ee.Number(ySeq.get(num))
        y2 = ee.Number(ySeq.get(num2))
        feat = ee.Feature(ee.Geometry.Polygon([[maxX, y2], [minX, y2], [minX, y1], [maxX, y1]]))
        return feat
    feats = ee.List.sequence(0, numFeats).map(latGridMapper)
    return ee.FeatureCollection(feats)

def makeLonGrid(minY, maxY, minX, maxX, size):

    ySeq = ee.List.sequence(minX, maxX, size)
    numFeats = ySeq.length().subtract(2)
    def longGridMapper(num):
        num = ee.Number(num)
        num2 = num.add(1)
        x1 = ee.Number(ySeq.get(num))
        x2 = ee.Number(ySeq.get(num2))
        feat = ee.Feature(ee.Geometry.Polygon([[x2, maxY], [x1, maxY], [x1, minY], [x2, minY]]))
        return feat
    feats = ee.List.sequence(0, numFeats).map(longGridMapper)
    return ee.FeatureCollection(feats)

def makeLonLatGrid(minY, maxY, minX, maxX, size):

    xSeq = ee.List.sequence(minX, maxX, size)
    ySeq = ee.List.sequence(minY, maxY, size)

    numFeatsY = ySeq.length().subtract(2)
    numFeatsX = xSeq.length().subtract(2)
    def lonLatMapper(y):
        y = ee.Number(y)
        y2 = y.add(1)
        y1_val = ee.Number(ySeq.get(y))
        y2_val = ee.Number(ySeq.get(y2))
        def inMapper(x):
            x = ee.Number(x)
            x2 = x.add(1)
            x1_val = ee.Number(xSeq.get(x))
            x2_val = ee.Number(xSeq.get(x2))
            return ee.Feature(
                ee.Geometry.Polygon([[x2_val, y2_val], [x1_val, y2_val], [x1_val, y1_val], [x2_val, y1_val]]))

        feat = ee.List.sequence(0, numFeatsX).map(inMapper)
        return feat
    feats = ee.List.sequence(0, numFeatsY).map(lonLatMapper)
    return ee.FeatureCollection(feats.flatten())

def getAncillary():

  demImage = ee.Image('USGS/SRTMGL1_003').rename('ELEVATION')
  slope = ee.Terrain.slope(demImage).rename('DEM_SLOPE')
  aspect = ee.Terrain.aspect(demImage).rename('ASPECT')
  bio = ee.Image('WORLDCLIM/V1/BIO').select(['bio01','bio12']).rename(['TEMPERATURE','RAINFALL'])

  return ee.Image.cat([demImage, slope, aspect, bio])

def getS2(startDate, endDate):
    if startDate is None:
        startDate = '2014-01-01'
    else:
        startDate = startDate
    if endDate is None:
        endDate = '2020-12-31'
    else:
        endDate = startDate

    def maskS2clouds(image):
        qa = image.select('QA60')

        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11

        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
                   qa.bitwiseAnd(cirrusBitMask).eq(0))

        # Return the masked and scaled data, without the QA bands.
        return image.updateMask(mask).divide(10000) \
            .select("B.*") \
            .copyProperties(image, ["system:time_start"])


    # Map the function over one year of data and take the median.
    # Load Sentinel-2 TOA reflectance data.
    collection = ee.ImageCollection('COPERNICUS/S2')\
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
      .map(maskS2clouds)

    return collection

def prepare(orbit):
  # Load the Sentinel-1 ImageCollection.
    return ee.ImageCollection('COPERNICUS/S1_GRD') \
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
    .filter(ee.Filter.eq('instrumentMode', 'IW')) \
    .filter(ee.Filter.eq('orbitProperties_pass', orbit))

def getS1Alt(options):
    if options is None:
        pass
    else:
        if 'targetBands' in options:
            targetBands = options['targetBands']
        else:
            targetBands = ['VV','VH','VH/VV']
        if 'focalSize' in options:
            focalSize = options['focalSize']
        else:
            focalSize = None
        if "mode" in options:
            mode = options['mode']
        else:
            mode = 'ASCENDING'
        if 'region' in options:
            region = options['region']
        else:
            region = None

    def s1Mapper(img):
        fmean = img.add(30).focal_mean(focalSize)
        ratio0 = fmean.select('VH').divide(fmean.select('VV')).rename('VH/VV').multiply(30)
        ratio1 = fmean.select('VV').divide(fmean.select('VH')).rename('VV/VH').multiply(30)
        return img.select().addBands(fmean).addBands(ratio0).addBands(ratio1)

    def s1Deg(img):
        pwr = ee.Image(10).pow(img.divide(10))
        pwr = pwr.select('VV').subtract(pwr.select('VH')).divide(pwr.select('VV').add(pwr.select('VH'))) \
            .rename('RFDI')
        ratio0 = img.select('VV').divide(img.select('VH')).rename('VV/VH')
        ratio1= img.select('VH').divide(img.select('VV')).rename('VH/VV')

        return img.addBands(pwr).addBands(ratio0).addBands(ratio1)

    data = ee.ImageCollection('COPERNICUS/S1_GRD') \
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
    .filter(ee.Filter.eq('orbitProperties_pass',mode))\
    .filter(ee.Filter.eq('instrumentMode', 'IW')) \

    if focalSize:
        data = data.map(s1Mapper)
    else:
        data = data.map(s1Deg)

    if region is not None:
        data = data.filterBounds(region)
    return data.select(targetBands)

def getS1(mode, focalSize):
    if focalSize is None:
        focalSize = 3
    if mode is None:
        mode = 'ASCENDING'
    def s1Mapper(img):
        fmean = img.add(30).focal_mean(focalSize)
        ratio = fmean.select('VH').divide(fmean.select('VV')).rename('ratio').multiply(30)
        return img.select().addBands(fmean).addBands(ratio)
    data = ee.ImageCollection('COPERNICUS/S1_GRD') \
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
    .filter(ee.Filter.eq('instrumentMode', 'IW')) \
    .select('V.') \
    .map(s1Mapper)

    return data

def prepareL4L5(image):
    bandList = ['B1', 'B2','B3','B4','B5','B7','B6']
    nameList = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'TEMP']
    scaling = [10000, 10000, 10000, 10000, 10000, 10000, 1000]
    scaled = ee.Image(image).select(bandList).rename(nameList).divide(ee.Image.constant(scaling))
    validQA = [66, 130, 68, 132]
    mask1 = ee.Image(image).select(['pixel_qa']).remap(validQA, ee.List.repeat(1, len(validQA)), 0)
    # Gat valid data mask, for pixels without band saturation
    mask2 = image.select('radsat_qa').eq(0)
    mask3 = image.select(bandList).reduce(ee.Reducer.min()).gt(0)
    # Mask hazy pixels
    mask4 = image.select("sr_atmos_opacity").lt(300)
    return image.addBands(scaled).updateMask(mask1.And(mask2).And(mask3).And(mask4))
    #combined = image.addBands(scaled).updateMask(mask1.And(mask2).And(mask3).And(mask4))
    #return combined.copyProperties(image).set('system:time_start', image.get('system:time_start'))

def prepareL7(image):
    bandList = ['B1', 'B2','B3','B4','B5','B7','B6']
    nameList = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'TEMP']
    scaling = [10000, 10000, 10000, 10000, 10000, 10000, 1000]
    scaled = ee.Image(image).select(bandList).rename(nameList).divide(ee.Image.constant(scaling))

    validQA = [66, 130, 68, 132]
    mask1 = ee.Image(image).select(['pixel_qa']).remap(validQA, ee.List.repeat(1, len(validQA)), 0)
    # Gat valid data mask, for pixels without band saturation
    mask2 = image.select('radsat_qa').eq(0)
    mask3 = image.select(bandList).reduce(ee.Reducer.min()).gt(0)
    # Mask hazy pixels
    mask4 = image.select("sr_atmos_opacity").lt(300)
    # Slightly erode bands to get rid of artifacts due to scan lines
    mask5 = ee.Image(image).mask().reduce(ee.Reducer.min()).focal_min(2.5)
    return image.addBands(scaled).updateMask(mask1.And(mask2).And(mask3).And(mask4).And(mask5))
    # combined = image.addBands(scaled).updateMask(mask1.And(mask2).And(mask3).And(mask4).And(mask5))
    # return combined.copyProperties(image).set('system:time_start', image.get('system:time_start'))

def prepareL8(image):
    bandList = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10']
    nameList = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'TEMP']
    scaling = [10000, 10000, 10000, 10000, 10000, 10000, 1000]

    validTOA = [66, 68, 72, 80, 96, 100, 130, 132, 136, 144, 160, 164]
    validQA = [322, 386, 324, 388, 836, 900]

    scaled = ee.Image(image).select(bandList).rename(nameList).divide(ee.Image.constant(scaling))
    mask1 = ee.Image(image).select(['pixel_qa']).remap(validQA, ee.List.repeat(1, len(validQA)), 0)
    mask2 = ee.Image(image).select('radsat_qa').eq(0)
    mask3 = ee.Image(image).select(bandList).reduce(ee.Reducer.min()).gt(0)
    mask4 = ee.Image(image).select(['sr_aerosol']).remap(validTOA, ee.List.repeat(1, len(validTOA)), 0)
    return ee.Image(image).addBands(scaled).updateMask(mask1.And(mask2).And(mask3).And(mask4))
    # combined = ee.Image(image).addBands(scaled).updateMask(mask1.And(mask2).And(mask3).And(mask4))
    # return combined.copyProperties(image).set('system:time_start', image.get('system:time_start'))

def generateCollection(geom, startDate, endDate):
    filteredL8 = (ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
                      .filter("WRS_ROW < 122") \
                      .filterBounds(geom) \
                      .map(prepareL8))

    filteredL7 = (ee.ImageCollection('LANDSAT/LE07/C01/T1_SR') \
                      .filter("WRS_ROW < 122") \
                      .filterBounds(geom) \
                      .map(prepareL7))

    # Originally not included in Noel's run
    filteredL4 = (ee.ImageCollection('LANDSAT/LT04/C01/T1_SR') \
                      .filter("WRS_ROW < 122") \
                      .filterBounds(geom) \
                      .map(prepareL4L5))
    filteredL5 = (ee.ImageCollection('LANDSAT/LT05/C01/T1_SR') \
                      .filter("WRS_ROW < 122") \
                      .filterBounds(geom) \
                      .map(prepareL4L5))

    mergedCollections = ee.ImageCollection(filteredL8).merge(filteredL7).merge(filteredL5).merge(filteredL4)
    return mergedCollections.filterDate(startDate, endDate)

def makeCcdImage(metadataFilter, segs, numberOfSegments,bandNames,inputFeatures, version):
    if metadataFilter is None:
        metadataFilter = 'z'
    if numberOfSegments is None:
        numberOfSegments = 6
    if bandNames is None:
        bandNames = ["BLUE","GREEN","RED","NIR","SWIR1","SWIR2","TEMP"]
    if segs is None:
        segs = ['S1','S2','S3','S4','S5','S6']
    if inputFeatures is None:
        inputFeatures = ["INTP", "SLP","PHASE","AMPLITUDE","RMSE"]
    if version is None:
        version = 'v2'

    ccdcCollection = ee.ImageCollection("projects/CCDC/" + version)

    # Get CCDC coefficients
    ccdcCollectionFiltered = ccdcCollection \
    .filterMetadata('system:index', 'starts_with',metadataFilter)

    # CCDC mosaic image
    ccdc = ccdcCollectionFiltered.mosaic()

    # Turn array image into image
    return ee.Image(ccdcUtils.buildCcdImage(ccdc, numberOfSegments, bandNames))


exports = {
    getLandsat: getLandsat,
    generateCollection: generateCollection,
    doIndices: doIndices,
    makeLatGrid: makeLatGrid,
    makeLonGrid: makeLonGrid,
    makeLonLatGrid: makeLonLatGrid,
    getAncillary: getAncillary,
    getS2: getS2,
    getS1: getS1,
    calcNDFI: calcNDFI,
    makeCcdImage: makeCcdImage,
    calcNDVI: calcNDVI,
    calcNBR: calcNBR,
    calcEVI: calcEVI,
    calcEVI2: calcEVI2,
    tcTrans: tcTrans,
    calcNDFI: calcNDFI
}



