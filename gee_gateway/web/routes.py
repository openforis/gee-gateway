from flask import request, jsonify
from flask_cors import CORS, cross_origin

from .. import app
from ..gee.utils import *
from ..gee.gee_exception import GEEException

import logging
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
