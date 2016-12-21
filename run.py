from gee_gateway import app

import logging

if __name__ == '__main__':

    logging.basicConfig(level=app.config['LOGGING_LEVEL'])
    logging.getLogger('flask_cors').level = app.config['LOGGING_LEVEL']
    logging.getLogger('gee_gateway').level = app.config['LOGGING_LEVEL']

    @app.route('/')
    def root():
        return app.send_static_file('index.html')

    app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'])