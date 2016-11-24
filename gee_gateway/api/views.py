import ee

from flask import request, jsonify
from flask_cors import CORS, cross_origin
from ee.ee_exception import EEException

from .. import app
from ..utils import *

@app.route('/image')
@cross_origin()
def image():
	"""  """
	values = {}
	try:
		imageName = request.args.get('imageName', None)
		Min = request.args.get('min', None)
		Max = request.args.get('max', None)
		bands = request.args.get('bands', None)
		visParams = visParamsBuilder(Min, Max, bands)
		if imageName:
			image = ee.Image(imageName)
			values = imageToMapId(image, visParams);
	except EEException as e:
		values = {
			'errMsg': e.message
		}
	return jsonify(values), 200

@app.route('/imageByMosaicCollection')
@cross_origin()
def imageByMosaicCollection():
	"""  """
	values = {}
	try:
		collectionName = request.args.get('collectionName', None)
		Min = request.args.get('min', None)
		Max = request.args.get('max', None)
		bands = request.args.get('bands', None)
		dateFrom = request.args.get('dateFrom', None)
		dateTo = request.args.get('dateTo', None)
		visParams = visParamsBuilder(Min, Max, bands)
		if collectionName:
			collection = ee.ImageCollection(collectionName)
			if (dateFrom and dateTo):
				filterDate = ee.Filter.date(dateFrom, dateTo)
				collection.filter(filterDate)
			firstImage = ee.Image(collection.first());
			values = imageToMapId(firstImage, visParams);
	except EEException as e:
		values = {
			'errMsg': e.message
		}
	return jsonify(values), 200