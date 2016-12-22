import logging

from flask import request, jsonify
from flask_cors import CORS, cross_origin

from .. import app
from ..gee.gee_exception import GEEException
from ..gee.utils import *


logger = logging.getLogger(__name__)

@app.route('/image', methods=['POST'])
@cross_origin(origins=app.config['CO_ORIGINS'])
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
    :<json String imageName: name of the image
    :<json Object visParams: visualization parameters
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            imageName = json.get('imageName', None)
            if imageName:
                visParams = json.get('visParams', None)
                values = imageToMapId(imageName, visParams)
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200

@app.route('/imageByMosaicCollection', methods=['POST'])
@cross_origin(origins=app.config['CO_ORIGINS'])
def imageByMosaicCollection():
    """
    .. :quickref: ImageCollection; Get the MapID of a EE ImageCollection.

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
                values = fistImageInMosaicToMapId(collectionName, visParams, dateFrom, dateTo)
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200

@app.route('/timeSeriesIndex', methods=['POST'])
@cross_origin(origins=app.config['CO_ORIGINS'])
def timeSeriesIndex():
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
        json = request.get_json()
        if json:
            collectionName = json.get('collectionNameTimeSeries', None)
            polygon = json.get('polygon', None)
            if collectionName and polygon:
                indexName = json.get('indexName', 'NDVI')
                scale = float(json.get('scale', 30))
                dateFrom = json.get('dateFromTimeSeries', None)
                dateTo = json.get('dateToTimeSeries', None)
                timeseries = getTimeSeriesByIndex(collectionName, indexName, scale, polygon, dateFrom, dateTo)
                values = {
                    'timeseries': timeseries
                }
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200
