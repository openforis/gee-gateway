from gee_gateway import app

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'])