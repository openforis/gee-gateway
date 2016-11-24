from flask import request, jsonify
from flask_cors import CORS, cross_origin

from .. import app
from ..gee.utils import *

@app.route('/image')
@cross_origin()
def image():
    """  """
    values = {}
    imageName = request.args.get('imageName', None)
    Min = request.args.get('min', None)
    Max = request.args.get('max', None)
    bands = request.args.get('bands', None)
    visParams = visParamsBuilder(Min, Max, bands)
    if imageName:
        values = imageToMapId(imageName, visParams);
    return jsonify(values), 200

@app.route('/imageByMosaicCollection')
@cross_origin()
def imageByMosaicCollection():
    """  """
    values = {}
    collectionName = request.args.get('collectionName', None)
    Min = request.args.get('min', None)
    Max = request.args.get('max', None)
    bands = request.args.get('bands', None)
    dateFrom = request.args.get('dateFrom', None)
    dateTo = request.args.get('dateTo', None)
    visParams = visParamsBuilder(Min, Max, bands)
    if collectionName:
        values = fistImageInMosaicToMapId(collectionName, visParams, dateFrom, dateTo);
    return jsonify(values), 200