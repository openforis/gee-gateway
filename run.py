import logging, argparse

from flask import Flask
from flask_cors import CORS

from gee_gateway import gee_gateway

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--gmaps_api_key', action='store', default='', help='Google Maps API key')
    parser.add_argument('--ee_account', action='store', default='', help='Google Earth Engine account')
    parser.add_argument('--ee_key_path', action='store', default='', help='Google Earth Engine key path')
    args, unknown = parser.parse_known_args()

    app = Flask(__name__, instance_relative_config=True, static_url_path="/static", static_folder="./static")
    app.config.from_object('config')
    app.config.from_pyfile('config.py', silent=True)

    app.config['GMAPS_API_KEY'] = args.gmaps_api_key

    gee_gateway_cors = CORS(gee_gateway, origins=app.config['CO_ORIGINS'])
    app.register_blueprint(gee_gateway)

    logging.basicConfig(level=app.config['LOGGING_LEVEL'])
    logging.getLogger('flask_cors').level = app.config['LOGGING_LEVEL']
    logging.getLogger('gee_gateway').level = app.config['LOGGING_LEVEL']

    app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'])
