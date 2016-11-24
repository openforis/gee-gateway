#################
#### imports ####
#################

import ee
from flask import Flask, request, jsonify

################
#### config ####
################

ee.Initialize()

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py', silent=True)
import api

########################
#### error handlers ####
########################

@app.errorhandler(404)
def not_found(error):
    app.logger.error('Not found: %s', (request.path))
    return jsonify({'errCode': '404'}), 200

@app.errorhandler(401)
def unauthorized(error):
    app.logger.error('Unauthorized: %s', (request.path))
    return jsonify({'errCode': '401'}), 200


@app.errorhandler(403)
def forbidden(error):
    app.logger.error('Forbidden: %s', (request.path))
    return jsonify({'errCode': '403'}), 200

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Internal Server Error: %s', (request.path))
    return jsonify({'errCode': '500'}), 200