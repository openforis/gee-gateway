from flask import request, jsonify

from .. import gee_gateway

@gee_gateway.errorhandler(404)
def not_found(error):
    gee_gateway.logger.error('Not found: %s', (request.path))
    return jsonify({'errCode': '404'}), 200

@gee_gateway.errorhandler(401)
def unauthorized(error):
    gee_gateway.logger.error('Unauthorized: %s', (request.path))
    return jsonify({'errCode': '401'}), 200


@gee_gateway.errorhandler(403)
def forbidden(error):
    gee_gateway.logger.error('Forbidden: %s', (request.path))
    return jsonify({'errCode': '403'}), 200

@gee_gateway.errorhandler(500)
def internal_server_error(error):
    gee_gateway.logger.error('Internal Server Error: %s', (request.path))
    return jsonify({'errCode': '500'}), 200