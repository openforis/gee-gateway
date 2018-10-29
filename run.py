import logging, argparse

from flask import Flask
from flask_cors import CORS
from flask_sslify import SSLify

from gee_gateway import gee_gateway, gee_initialize

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--gmaps_api_key', action='store', default='', help='Google Maps API key')
    parser.add_argument('--ee_account', action='store', default='', help='Google Earth Engine account')
    parser.add_argument('--ee_key_path', action='store', default='', help='Google Earth Engine key path')
    parser.add_argument('--ee_token_enabled', action='store_false')
    args, unknown = parser.parse_known_args()

    app = Flask(__name__, instance_relative_config=True, static_url_path="/static", static_folder="./static")
    app.config.from_object('config')
    app.config.from_pyfile('config.py', silent=True)

    app.config['GMAPS_API_KEY'] = args.gmaps_api_key
    app.config['EE_ACCOUNT'] = args.ee_account
    app.config['EE_KEY_PATH'] = args.ee_key_path
    app.config['EE_TOKEN_ENABLED'] = args.ee_token_enabled

    if not args.ee_token_enabled:
        gee_initialize(ee_account=args.ee_account, ee_key_path=args.ee_key_path)
    gee_gateway_cors = CORS(gee_gateway, origins=app.config['CO_ORIGINS'])
    app.register_blueprint(gee_gateway)

    logging.basicConfig(level=app.config['LOGGING_LEVEL'])
    logging.getLogger('flask_cors').level = app.config['LOGGING_LEVEL']
    logging.getLogger('gee_gateway').level = app.config['LOGGING_LEVEL']
    sslify = SSLify(app)
    #app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'])
    #app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'], ssl_context='adhoc')
