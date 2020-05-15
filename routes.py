from gee.gee_exception import GEEException
from gee.utils import *
from gee.inputs import *
from gee.dates import *
from gee.ccdc import *
from planet.utils import *
from flask import Flask, request, jsonify, render_template, json, current_app, send_file, make_response
from flask_cors import CORS, cross_origin
import logging
from logging.handlers import RotatingFileHandler
import urllib


logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'gee-gateway-nginx.log', maxBytes=10485760, backupCount=10)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

gee_gateway = Flask(__name__, instance_relative_config=True,
                    static_url_path="/static", static_folder="./static")
gee_gateway.config.from_object('config')
gee_gateway.config.from_pyfile('config.py', silent=True)

@gee_gateway.before_request
def before():
    ee_user_token = None
    ee_account = current_app.config.get('EE_ACCOUNT')
    ee_key_path = current_app.config.get('EE_KEY_PATH')
    if current_app.config.get('EE_TOKEN_ENABLED'):
        if 'sepal-user' in request.headers:
            user = json.loads(request.headers['sepal-user'])
            googleTokens = user.get('googleTokens', None)
            if googleTokens:
                ee_user_token = googleTokens['accessToken']
                initialize(ee_user_token=ee_user_token,
                           ee_account=ee_account, ee_key_path=ee_key_path)
        else:
            initialize(ee_account=ee_account, ee_key_path=ee_key_path)
    else:
        initialize(ee_account=ee_account, ee_key_path=ee_key_path)


@gee_gateway.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@gee_gateway.route('/image', methods=['POST'])
def image():
    """ Return

    .. :quickref: Image; Get the MapID of a EE Image.

    **Example request**:

    .. code-block:: javascript

        {
            imageName: "XXX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX",
                gamma: 0.0,
                palette: "XX"
           }
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String imageName: name of the image
    :<json Object visParams: visualization parameters
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        jsonp = request.get_json()
        if jsonp:
            imageName = jsonp.get('imageName', None)
            visParams = jsonp.get('visParams', {})
            values = imageToMapId(imageName, visParams)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/firstImageByMosaicCollection', methods=['POST'])
def firstImageByMosaicCollection():
    """
    .. :quickref: firstImageByMosaicCollection; Get the MapID of a EE firstImageByMosaicCollection.

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX",
                gamma: 0.0
            },
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json Object visParams: visualization parameters
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionName', None)
            if collectionName:
                visParams = json.get('visParams', None)
                dateFrom = json.get('dateFrom', None)
                dateTo = json.get('dateTo', None)
                values = firstImageInMosaicToMapId(
                    collectionName, visParams, dateFrom, dateTo)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/meanImageByMosaicCollections', methods=['POST'])
def meanImageByMosaicCollections():
    """
    .. :quickref: meanImageByMosaicCollections; Get the MapID of a EE meanImageByMosaicCollections.

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX",
                gamma: 0.0
            },
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json Object visParams: visualization parameters
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionName', None)
            if collectionName:
                visParams = json.get('visParams', None)
                dateFrom = json.get('dateFrom', None)
                dateTo = json.get('dateTo', None)
                values = meanImageInMosaicToMapId(
                    collectionName, visParams, dateFrom, dateTo)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/imageByMosaicCollection', methods=['POST'])
def imageByMosaicCollection():
    """
    .. :quickref: @gee_gateway.route('/imageByMosaicCollection', methods=['POST']); 
    Get the MapID of a EE @gee_gateway.route('/imageByMosaicCollection', methods=['POST']).

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX"
            }
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json Object visParams: valid python formatted EE vision parameters
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionName', None)
            if collectionName:
                visParams = json.get('visParams', None)
                dateFrom = json.get('dateFrom', None)
                dateTo = json.get('dateTo', None)
                values = filteredImageByIndexToMapId(
                    dateFrom, dateTo, collectionName)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/cloudMaskImageByMosaicCollection', methods=['POST'])
def cloudMaskImageByMosaicCollection():
    """
    .. :quickref: cloudMaskImageByMosaicCollection; Get the MapID of a EE cloudMaskImageByMosaicCollection.

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX"
            },
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json Object visParams: visualization parameters
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionName', None)
            if collectionName:
                visParams = json.get('visParams', None)
                dateFrom = json.get('dateFrom', None)
                dateTo = json.get('dateTo', None)
                values = firstCloudFreeImageInMosaicToMapId(
                    collectionName, visParams, dateFrom, dateTo)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/meanImageByMosaicCollection', methods=['POST'])
def meanImageByMosaicCollection():
    """
    .. :quickref: meanImageByMosaicCollection; Get the MapID of a EE meanImageByMosaicCollection.

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX"
            },
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json Object visParams: visualization parameters
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionName', None)
            if collectionName:
                visParams = json.get('visParams', None)
                dateFrom = json.get('dateFrom', None)
                dateTo = json.get('dateTo', None)
                values = filteredImageInMosaicToMapId(
                    collectionName, visParams, dateFrom, dateTo)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/getCHIRPSImage', methods=['POST'])
def getCHIRPSImage():
    """
    .. :quickref: getCHIRPSImage; Get the MapID of a EE CHIRPS Image.

    **Example request**:

    .. code-block:: javascript

        {
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            dateFrom = json.get('dateFrom', None)
            dateTo = json.get('dateTo', None)
            values = filteredImageInCHIRPSToMapId(dateFrom, dateTo)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/ImageCollectionbyIndex', methods=['POST'])
def ImageCollectionbyIndex():
    """
    .. :quickref: ImageCollectionbyIndex; Get the MapID of a EE LANDSAT ImageCollection by requested Index.

    **Example request**:

    .. code-block:: javascript

        {
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD",
            index: "xx"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :<json String index: index requested, ie: NDVI, EVI, etc...
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            dateFrom = json.get('dateFrom', None)
            if not dateFrom:
                dateFrom = None
            dateTo = json.get('dateTo', None)
            if not dateTo:
                dateTo = None
            index = json.get('index', 'ndvi')
            values = filteredImageByIndexToMapId(dateFrom, dateTo, index)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/timeSeriesIndex', methods=['POST'])
def timeSeriesIndex():
    """
    .. :quickref: TimeSeries; Get the timeseries for a specific ImageCollection index, date range and a polygon OR a point

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            indexName: "XX"
            scale: 0.0,
            geometry: [
                [0.0, 0.0],
                [...]
            ] OR [0.0, 0.0],
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            timeseries: [
                [0, 0.0],
                ...
            ]
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json String index: name of the index:  (e.g. NDVI, NDWI, NVI)
    :<json Float scale: scale in meters of the projection
    :<json Array polygon: the region over which to reduce data
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionNameTimeSeries', None)
            geometry = json.get('polygon', None)  # deprecated
            if not geometry:
                geometry = json.get('geometry', None)
            if collectionName and geometry:
                #indexName = json.get('indexName', 'NDVI')
                indexName = json.get('indexName', None)
                scale = float(json.get('scale', 30))
                dateFrom = json.get('dateFromTimeSeries', None)
                dateTo = json.get('dateToTimeSeries', None)
                reducer = json.get('reducer', None)
                timeseries = getTimeSeriesByCollectionAndIndex(
                    collectionName, indexName, scale, geometry, dateFrom, dateTo, reducer)
                values = {
                    'timeseries': timeseries
                }
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/timeSeriesIndex2', methods=['POST'])
def timeSeriesIndex2():
    """
    .. :quickref: TimeSeries2; Get the timeseries for a specific ImageCollection index, date range and a polygon OR a point

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            indexName: "XX"
            scale: 0.0,
            geometry: [
                [0.0, 0.0],
                [...]
            ] OR [0.0, 0.0],
            dateFromTimeSeries: "YYYY-MM-DD",
            getTimeSeriesByIndex2: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            timeseries: [
                [0, 0.0],
                ...
            ]
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json String index: name of the index:  (e.g. NDVI, NDWI, NVI)
    :<json Float scale: scale in meters of the projection
    :<json Array polygon: the region over which to reduce data
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            geometry = json.get('polygon', None)  # deprecated
            if not geometry:
                geometry = json.get('geometry', None)
            if geometry:
                indexName = json.get('indexName', 'NDVI')
                scale = float(json.get('scale', 30))
                dateFrom = json.get('dateFromTimeSeries', None)
                dateTo = json.get('dateToTimeSeries', None)
                timeseries = getTimeSeriesByIndex2(
                    indexName, scale, geometry, dateFrom, dateTo)
                values = {
                    'timeseries': timeseries
                }
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/timeSeriesIndex3', methods=['POST'])
def timeSeriesIndex3():
    """
    .. :quickref: TimeSeries3; Get the timeseries for a specific ImageCollection index, date range and a polygon OR a point

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            indexName: "XX"
            scale: 0.0,
            geometry: [
                [0.0, 0.0],
                [...]
            ] OR [0.0, 0.0],
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            timeseries: [
                [0, 0.0],
                ...
            ]
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json String index: name of the index:  (e.g. NDVI, NDWI, NVI)
    :<json Float scale: scale in meters of the projection
    :<json Array polygon: the region over which to reduce data
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            geometry = json.get('polygon', None)  # deprecated
            if not geometry:
                geometry = json.get('geometry', None)
            if geometry:
                indexName = json.get('indexName', 'NDVI')
                scale = float(json.get('scale', 30))
                dateFrom = json.get('dateFrom', None)
                dateTo = json.get('dateTo', None)
                timeseries = getTimeSeriesByIndex2(
                    indexName, scale, geometry, dateFrom, dateTo)
                values = {
                    'timeseries': timeseries
                }
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/timeSeriesForPoint', methods=['POST'])
def timeSeriesForPoint():
    """
    .. :quickref: TimeSeries ForPoint; Get the timeseries for LANDSAT, date range and a point

    **Example request**:

    .. code-block:: javascript

        {
            point:  [0.0, 0.0],
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            timeseries: [
                [0, 0.0],
                ...
            ]
        }

    :reqheader Accept: application/json
    :<json Array point: the point which to reduce data
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            geometry = json.get('point', None)
            if geometry:
                timeseries = getTimeSeriesForPoint(geometry)
                values = {
                    'timeseries': timeseries
                }
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/timeSeriesAssetForPoint', methods=['POST'])
def timeSeriesAssetForPoint():
    """
    .. :quickref: TimeSeries For predefined asset; Get the timeseries for a predefined EE asset, date range and a point

    **Example request**:

    .. code-block:: javascript

        {
            point:  [0.0, 0.0],
            dateFromTimeSeries: "YYYY-MM-DD",
            dateToTimeSeries: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            timeseries: [
                [0, 0.0],
                ...
            ]
        }

    :reqheader Accept: application/json
    :<json Array point: the point which to reduce data
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            geometry = json.get('point', None)
            dateFrom = json.get('dateFromTimeSeries', None)
            dateTo = json.get('dateToTimeSeries', None)
            timeseries = getTimeSeriesAssetForPoint(geometry, dateFrom, dateTo)
            print("have vals")
            values = {
                'timeseries': timeseries
            }
            print(str(values))
        else:
            logger.error("i didn't have json")
    except GEEException as e:
        logger.error(e)
        values = {
            'errMsg': e
        }
    return jsonify(values), 200


@gee_gateway.route('/timeSeriesIndexGet', methods=['GET'])
def timeSeriesIndexGet():
    """
    .. :quickref: TimeSeries; Get the timeseries for a specific ImageCollection index, date range and polygon

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            indexName: "XX"
            scale: 0.0,
            polygon: [
                [0.0, 0.0],
                [...]
            ],
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            timeseries: [
                [0, 0],
                ...
            ]
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json String index: name of the index:  (e.g. NDVI, NDWI, NVI)
    :<json Float scale: scale in meters of the projection
    :<json Array polygon: the region over which to reduce data
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        collectionName = request.args.get('collectionNameTimeSeries', None)
        polygon = ast.literal_eval(urllib.unquote(
            request.args.get('polygon', None)).decode('utf8'))
        indexName = request.args.get('indexName', 'NDVI')
        scale = float(request.args.get('scale', 30))
        dateFrom = request.args.get('dateFromTimeSeries', None)
        dateTo = request.args.get('dateToTimeSeries', None)
        reducer = request.args.get('reducer', None)
        timeseries = getTimeSeriesByIndex(
            collectionName, indexName, scale, polygon, dateFrom, dateTo, reducer)
        values = {
            'timeseries': timeseries
        }
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/getStats', methods=['POST'])
def getStats():
    """
    .. :quickref: getStats; Get the population and elevation for a polygon

    **Example request**:

    .. code-block:: javascript

        {
            paramType: "XX",
            paramValue: [
                [0.0, 0.0],
                [...]
            ]
        }

    **Example response**:

    .. code-block:: javascript

        {maxElev: 1230, minElev: 1230, pop: 0}

    :reqheader Accept: application/json
    :<json String paramType: basin, landscape, or ''
    :<json Array polygon: the region over which to reduce data
    :resheader Content-Type: application/json
    """
    try:
        values = {}
        json = request.get_json()
        paramType = json.get('paramType', None)
        paramValue = json.get('paramValue', None)
        values = getStatistics(paramType, paramValue)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/asterMosaic', methods=['POST'])
def asterMosaic():
    values = {}
    try:
        json = request.get_json()
        if json:
            visParams = json.get('visParams', None)
            dateFrom = json.get('dateFrom', None)
            dateTo = json.get('dateTo', None)
            values = getAsterMosaic(visParams, dateFrom, dateTo)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/ndviChange', methods=['POST'])
def ndviChange():
    values = {}
    try:
        json = request.get_json()
        if json:
            visParams = json.get('visParams', None)
            yearFrom = json.get('yearFrom', None)
            yearTo = json.get('yearTo', None)
            values = getNdviChange(visParams, yearFrom, yearTo)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/Landsat5Filtered', methods=['POST'])
def Landsat5Filtered():
    """
    .. :quickref: Landsat5Filtered; Get the MapID of a EE LANDSAT5 filtered ImageCollection by requested Index.

    **Example request**:

    .. code-block:: javascript

        {
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD",
            cloudLessThan: nn,
            bands: "B4,B5,B3",
            min: "0.03,0.01,0.05",
            max": "0.45,0.5,0.4"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :<json String cloudLessThan: cloud filter number
    :<json String bands: bands
    :<json String min: min
    :<json String max: max
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            values = getFiltered('LANDSAT/LT05/C01/T1', json, 50)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/Landsat7Filtered', methods=['POST'])
def Landsat7Filtered():
    """
    .. :quickref: Landsat7Filtered; Get the MapID of a EE LANDSAT7 filtered ImageCollection by requested Index.

    **Example request**:

    .. code-block:: javascript

        {
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD",
            cloudLessThan: nn,
            bands: "B4,B5,B3",
            min: "0.03,0.01,0.05",
            max": "0.45,0.5,0.4"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :<json String cloudLessThan: cloud filter number
    :<json String bands: bands
    :<json String min: min
    :<json String max: max
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            values = getFiltered('LANDSAT/LE07/C01/T1', json, 60)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/Landsat8Filtered', methods=['POST'])
def Landsat8Filtered():
    """
    .. :quickref: Landsat8Filtered; Get the MapID of a EE LANDSAT8 filtered ImageCollection by requested Index.

    **Example request**:

    .. code-block:: javascript

        {
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD",
            cloudLessThan: nn,
            bands: "B4,B5,B3",
            min: "0.03,0.01,0.05",
            max": "0.45,0.5,0.4"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :<json String cloudLessThan: cloud filter number
    :<json String bands: bands
    :<json String min: min
    :<json String max: max
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            values = getFiltered('LANDSAT/LC08/C01/T1_RT', json, 50)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/FilteredSentinel', methods=['POST'])
def FilteredSentinel():
    """
    .. :quickref: FilteredSentinel; Get the MapID of a EE Sentinel filtered ImageCollection by requested Index.

    **Example request**:

    .. code-block:: javascript

        {
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD",
            cloudLessThan: nn,
            bands: "B4,B5,B3",
            min: "0.03,0.01,0.05",
            max": "0.45,0.5,0.4"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :<json String cloudLessThan: cloud filter number
    :<json String bands: bands
    :<json String min: min
    :<json String max: max
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            dateFrom = json.get('dateFrom', None)
            dateTo = json.get('dateTo', None)
            cloudLessThan = json.get('cloudLessThan', 90)
            bands = json.get('bands', 'B4,B5,B3')
            min = json.get('min', '0.03,0.01,0.05')
            max = json.get('max', '0.45,0.5,0.4')
            visParams = {
                'min': min,
                'max': max,
                'bands': bands
            }
            values = filteredSentinelComposite(
                visParams, dateFrom, dateTo, cloudLessThan)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/ImageCollectionAsset', methods=['POST'])
def ImageCollectionAsset():
    """
    .. :quickref: FilteredSentinel; Get the MapID of a EE Sentinel filtered ImageCollection by requested Index.

    **Example request**:

    .. code-block:: javascript

        {
            imageName: "xx",
            ImageCollectionAsset: "xx",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX"
            }
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String imageName: if requesting an image asset send the image name
    :<json String ImageCollectionAsset: if requesting an imageCollection asset send the ImageCollection Asset name
    :<json Object visParams: visParams
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collection = ''
            if 'imageName' in json:
                collection = json.get('imageName', '')
            else:
                collection = json.get('ImageCollectionAsset', '')
            visParams = json.get('visParams', {})
            values = getImageCollectionAsset(collection, visParams)
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


def getFiltered(collectionName, json, simpleCompositVariable):
    dateFrom = json.get('dateFrom', None)
    dateTo = json.get('dateTo', None)
    cloudLessThan = json.get('cloudLessThan', 90)
    bands = json.get('bands', 'B4,B5,B3')
    min = json.get('min', '0.03,0.01,0.05')
    max = json.get('max', '0.45,0.5,0.4')
    visParams = {
        'min': min,
        'max': max,
        'bands': bands
    }
    return filteredImageCompositeToMapId(collectionName, visParams, dateFrom, dateTo, cloudLessThan, simpleCompositVariable)


@gee_gateway.route('/getPlanetTile', methods=['POST'])
def getPlanetTile():
    """ To do: add definition """
    values = {}
    try:
        json = request.get_json()
        apiKey = json.get('apiKey')
        geometry = json.get('geometry')
        start = json.get('dateFrom')
        end = json.get('dateTo', None)
        layerCount = json.get('layerCount', 1)
        itemTypes = json.get('itemTypes', ['PSScene3Band', 'PSScene4Band'])
        values = getPlanetMapID(apiKey, geometry, start,
                                end, layerCount, itemTypes)
    except Exception as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/getAvailableBands', methods=['POST'])
def getAvailableBands():
    """ To do: add definition """
    logger.error("Debugging getAvailableBands")
    values = {}
    try:
        json = request.get_json()
        if json:
            imageCollectionName = json.get('imageCollection', None)
            imageName = json.get('image', None)
            if imageCollectionName is None:
                values = listAvailableBands(imageName, True)
            else:
                logger.error("getAvailableBands else")
                actualName = getActualCollection(imageCollectionName)
                logger.error(actualName + "spaces?")
                values = listAvailableBands(actualName, False)
        else:
            raise Exception(
                "Need either image or imageCollection parameter containing the full name")
    except Exception as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


def getActualCollection(name):
    if name == "LANDSAT5":
        return "LANDSAT/LT05/C01/T1"
    elif name == "LANDSAT7":
        return "LANDSAT/LE07/C01/T1"
    elif name == "LANDSAT8":
        return "LANDSAT/LC08/C01/T1_RT"
    elif name == "Sentinel2":
        return "COPERNICUS/S2"
    else:
        return name

@gee_gateway.route('/getImagePlotDegradition', methods=['POST'])
def getImagePlotDegradition():
    values = {}
    try:
        json = request.get_json()
        if json:
            geometry = json.get('geometry')
            start = json.get('start')
            end = json.get('end')
            band = json.get('band', 'NDFI')
            dataType = json.get('dataType', 'landsat')
            if dataType == 'landsat':
                values = {
                    'timeseries': getDegradationPlotsByPoint(geometry, start, end, band)
                }
            else:
                values = {
                    'timeseries': getDegradationPlotsByPointS1(geometry, start, end, band)
                }
        else:
            raise Exception(
                "Need either image or imageCollection parameter containing the full name")
    except Exception as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200

@gee_gateway.route('/getDegraditionTileUrl', methods=['POST'])
def getDegraditionTileUrl():
    values = {}
    try:
        json = request.get_json()
        if json:
            imageDate = json.get('imageDate', None)
            geometry = json.get('geometry')
            stretch = json.get('stretch', 321)
            visParams = {}
            if stretch == 321:
                visParams = {'bands': 'RED,GREEN,BLUE', 'min': 0, 'max': 1400}
            elif stretch == 543:
                visParams ={'bands': 'SWIR1,NIR,RED', 'min': 0, 'max': 7000}
            elif stretch == "SAR":
                visParams = {'bands':'VV,VH,VV/VH', 'min':'-15,-25,.40', 'max': '0,-10,1', 'gamma': '1.6' }
            tparams = json.get('visParams', "")

            dataType = json.get('dataType', 'landsat')
            if tparams != "":
                visParams = tparams

            if dataType == 'landsat':
                values = {
                    "url": getDegraditionTileUrlByDate(geometry, imageDate, visParams)#(getDegraditionTileUrlByDateS1(geometry, imageDate, visParams),getDegraditionTileUrlByDate(geometry, imageDate, visParams))[dataType == "landsat"]
                }
            else:
                values = {
                    "url": getDegraditionTileUrlByDateS1(geometry, imageDate, visParams)
                }
        else:
            raise Exception(
                "Need either imageDate and geometry parameters")
    except Exception as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/FilteredSentinelSAR', methods=['POST'])
def FilteredSentinelSAR():
    values = {}
    try:
        json = request.get_json()
        if json:
            dateFrom = json.get('dateFrom', None)
            dateTo = json.get('dateTo', None)
            bands = json.get('bands', 'VH,VV,VH/VV')
            min = json.get('min', '0')
            max = json.get('max', '0.3')
            dbValue = json.get('dbValue', False)
            visParams = {
                'min': min,
                'max': max,
                'bands': bands
            }
            values = filteredSentinelSARComposite(visParams, dbValue, dateFrom, dateTo)
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200
############################### TimeSync ##############################


@gee_gateway.route('/ts')
def tsIndex():
    return 'TimeSync v4.0'


@gee_gateway.route('/ts/images/<lng>/<lat>/<int:year>', methods=['GET'])
def getAllLandsatImagesForPlot(lng, lat, year):
    values = {}
    try:
        if year <= 1980:
            year = None

        values = getLandsatImages((float(lng), float(lat)), year)

    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
    return jsonify(values), 200


@gee_gateway.route('/ts/chip/<lng>/<lat>/<int:year>/<int:day>/<vis>', methods=['GET'])
def getChipForYearByTargetDay(lng, lat, year, day, vis):
    """
    get image chip for specified year for plot coordinate.
    """

    values = {}
    try:
        values = getLandsatChipForYearByTargetDay(
            (float(lng), float(lat)), year, day, vis)
        fp = urllib.request.urlopen(values.get('chip_url'))
        fname = '%s_%s.png' % (values.get('iid'), values.get('doy'))
        response = make_response(send_file(
            fp, mimetype='image/png', as_attachment=True, attachment_filename=fname))
        response.headers['doy'] = values.get('doy')
        response.headers['iid'] = values.get('iid')
        response.headers['chip_url'] = values.get('chip_url')
        return response, 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500


@gee_gateway.route('/ts/image_chip/<lng>/<lat>/<path:iid>/<vis>/<int:size>', methods=['GET'])
def getImageChip(lng, lat, iid, vis, size=255):
    """
    get image chip for specified image

    @param
        {
            "lat":
            "lng":
            "iid": LANDSAT/LE07/C01/T1_SR/LE07_045030_20000122
            "vis":
        }
    @return
    """

    values = {}
    try:
        values = createChip(iid, (float(lng), float(lat)), vis, size)
        fp = urllib.request.urlopen(values.get('chip_url'))
        fname = '%s_%s.png' % (values.get('iid'), values.get('doy'))
        response = make_response(send_file(
            fp, mimetype='image/png', as_attachment=True, attachment_filename=fname))
        response.headers['doy'] = values.get('doy')
        response.headers['iid'] = values.get('iid')
        response.headers['chip_url'] = values.get('chip_url')
        return response, 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500
    # return jsonify(values), 200


@gee_gateway.route('/ts/chip_url/<lng>/<lat>/<int:year>/<int:day>/<vis>', methods=['GET'])
def getChipForYearByTargetDayURL(lng, lat, year, day, vis):
    """
    get image chip for specified year for plot coordinate.
    """

    values = {}
    try:
        values = getLandsatChipForYearByTargetDay(
            (float(lng), float(lat)), year, day, vis)
        return values.get('chip_url'), 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500


@gee_gateway.route('/ts/image_chip_url/<lng>/<lat>/<path:iid>/<vis>/<int:size>', methods=['GET'])
def getImageChipURL(lng, lat, iid, vis, size=255):
    """
    get image chip for specified image

    @param
        {
            "lat":
            "lng":
            "iid": LANDSAT/LE07/C01/T1_SR/LE07_045030_20000122
            "vis":
        }
    @return
    """

    values = {}
    try:
        values = createChip(iid, (float(lng), float(lat)), vis, size)
        return jsonify(values), 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500
    # return jsonify(values), 200


@gee_gateway.route('/ts/image_chip_xyz/<lng>/<lat>/<path:iid>/<vis>/<int:size>', methods=['GET'])
def getImageChipXYZ(lng, lat, iid, vis, size=255):
    """
    get image chip for specified image

    @param
        {
            "lat":
            "lng":
            "iid": LANDSAT/LE07/C01/T1_SR/LE07_045030_20000122
            "vis":
        }
    @return
    """

    values = {}
    try:
        values = createChipXYZ(iid, (float(lng), float(lat)), vis, size)
        return jsonify(values), 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500
    # return jsonify(values), 200


# TODO: refactory the next three methods
@gee_gateway.route('/ts/spectrals/<lng>/<lat>', methods=['GET'])
def getPlotSpectrals(lng, lat):
    """
    get spectral data for all the landsat images.

    @param
        {
            "lat":
            "lng":
        }
    @return
    """
    values = {}
    try:
        timeseries = getTsTimeSeriesForPoint((float(lng), float(lat)))
        values = {
            'timeseries': timeseries
        }
        return jsonify(values), 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500


@gee_gateway.route('/ts/spectrals/year/<int:year>/<lng>/<lat>', methods=['GET'])
def getPlotSpectralsByYear(year, lng, lat):
    """
    get spectral data for all the landsat images closest to the target day

    @param
        {
            "lat":
            "lng":
        }
    @return
    """
    values = {}
    try:
        # timeseries = getTsTimeSeriesForPoint((float(lng), float(lat)))
        timeseries = getTsTimeSeriesForPointByYear(
            (float(lng), float(lat)), int(year))
        values = {
            'timeseries': timeseries
        }
        return jsonify(values), 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500


@gee_gateway.route('/ts/spectrals/day/<int:julday>/<lng>/<lat>', methods=['GET'])
def getPlotSpectralsByJulday(julday, lng, lat):
    """
    get spectral data for all the landsat images closest to the target day

    @param
        {
            "lat":
            "lng":
        }
    @return
    """
    values = {}
    try:
        # timeseries = getTsTimeSeriesForPoint((float(lng), float(lat)))
        timeseries = getTsTimeSeriesForPointByTargetDay(
            (float(lng), float(lat)), int(julday))
        values = {
            'timeseries': timeseries
        }
        return jsonify(values), 200
    except GEEException as e:
        logger.error(str(e))
        values = {
            'errMsg': str(e)
        }
        return jsonify(values), 500
