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
    """  """
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
    """  """
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