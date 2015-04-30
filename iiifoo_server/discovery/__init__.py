__author__ = 'hashim'

from flask import Blueprint


discovery = Blueprint('discovery', __name__, template_folder='../templates')


import discovery_views
