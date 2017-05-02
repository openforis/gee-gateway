from flask import Blueprint

gee_gateway = Blueprint('gee_gateway', __name__, template_folder='templates', static_folder='static', static_url_path='/static/gee_gateway')

import gee, web
