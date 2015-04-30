from flask import Blueprint


viewing = Blueprint('viewing', __name__, template_folder='../templates')


import basic_views
import iiif_metadata_api_views
