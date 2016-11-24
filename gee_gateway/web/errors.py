from flask import request, jsonify

from .. import app

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