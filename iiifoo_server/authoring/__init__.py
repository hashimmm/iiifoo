__author__ = 'hashim'

from flask import Blueprint


authoring = Blueprint('authoring', __name__, template_folder='../templates')


import authoring_views
