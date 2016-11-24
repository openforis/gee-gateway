from flask import request, jsonify
from flask_cors import CORS, cross_origin

from .. import app
from ..gee.utils import *

@app.route('/image', methods=['POST'])
@cross_origin()
def image():
    """  """
    values = {}
    json = request.get_json()
    if json:
        imageName = json.get('imageName', None)
        if imageName:
            visParams = json.get('visParams', None)
            values = imageToMapId(imageName, visParams);
    return jsonify(values), 200

@app.route('/imageByMosaicCollection', methods=['POST'])
@cross_origin()
def imageByMosaicCollection():
    """  """
    values = {}
    json = request.get_json()
    if json:
        collectionName = json.get('collectionName', None)
        if collectionName:
            visParams = json.get('visParams', None)
            dateFrom = json.get('dateFrom', None)
            dateTo = json.get('dateTo', None)
            values = fistImageInMosaicToMapId(collectionName, visParams, dateFrom, dateTo)
    return jsonify(values), 200