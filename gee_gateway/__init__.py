from flask import Blueprint

gee_gateway = Blueprint('gee_gateway', __name__, template_folder='templates', static_folder='static', static_url_path='/static/gee_gateway')

import gee, web

def gee_initialize(ee_account='', ee_key_path=''):
    gee.utils.initialize(ee_account=ee_account, ee_key_path=ee_key_path)