from flask import Flask, request, jsonify

app = Flask(__name__, instance_relative_config=True, static_url_path="/static", static_folder="../static")
app.config.from_object('config')
app.config.from_pyfile('config.py', silent=True)

import web
import gee