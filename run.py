from gee_gateway import app
import logging, argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--gmaps_api_key', action='store', default='', help='Google Maps API key')
    parser.add_argument('--ee_account', action='store', default='', help='Google Earth Engine account')
    parser.add_argument('--ee_key_path', action='store', default='', help='Google Earth Engine key path')
    args, unknown = parser.parse_known_args()

    app.config['GMAPS_API_KEY'] = args.gmaps_api_key

    logging.basicConfig(level=app.config['LOGGING_LEVEL'])
    logging.getLogger('flask_cors').level = app.config['LOGGING_LEVEL']
    logging.getLogger('gee_gateway').level = app.config['LOGGING_LEVEL']

    @app.route('/static/<path:path>')
    def send(path):
        return send_from_directory('static', path)

    app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'])