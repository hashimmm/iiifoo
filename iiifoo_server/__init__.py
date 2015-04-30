"""This package contains the flask application that runs as the HTTP server.

A lot of view functions have two code paths: this is because originally the
two different 'source types' had different URIs, but then they were merged to
use the same URIs/APIs. This might be refactored sooner or later to be neater.
"""
import logging

from flask import Flask, request, jsonify, g

try:
    import settings  # NOTE: DO NOT CHANGE TO `from settings import get`
except ImportError:
    print "Unable to find `settings.py`. Please run "\
          "`python populate_settings.py` to prep configurations first."
    import sys
    sys.exit(1)

import exception
from dbmodels import db


fh = logging.FileHandler('iiifoo_server.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))


def register_hooks(app):
    if settings.get("server_debug"):
        @app.before_request
        def log_request():
                app.logger.debug(
                    "Received request: '{}'\n\n "
                    "Args: {}\n\n Form: {}\n\n "
                    "JSON: {}\n\n Data: {}\n\n".format(
                        request, request.args, request.form, request.json,
                        request.data
                    )
                )


def attach_models(app):
    engine_str = settings.get('db_dialect') + "://"
    tempstr = settings.get('db_user')
    engine_str += tempstr if tempstr else ""
    tempstr = settings.get('db_pass')
    if tempstr:
        engine_str += ":"
        engine_str += tempstr
    tempstr = settings.get("db_host")
    if tempstr:
        engine_str += "@"
        engine_str += tempstr
    tempstr = settings.get("db_port")
    if tempstr:
        engine_str += ":"
        engine_str += tempstr
    engine_str += "/"
    engine_str += settings.get('db_name')

    app.config['SQLALCHEMY_DATABASE_URI'] = engine_str
    db.init_app(app)
    db.create_all(app=app)


def attach_loggers(app):
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(fh)


def register_blueprints(app):
    from iiifoo_server import discovery, viewing, authoring
    # enable read-only
    app.register_blueprint(viewing.viewing, url_prefix='')
    # enable authoring
    app.register_blueprint(authoring.authoring, url_prefix='')
    # enable sitemaps
    app.register_blueprint(discovery.discovery, url_prefix='')


def register_errorhandlers(app):
    @app.errorhandler(exception.IiifooError)
    def handle_mira_errors(error):
        """Log whenever a known IiiFooError occurs and return an appropriate response.

        Once transaction IDs are supported, will log them.

        :param error: The exception that was caught
        :type error: stor.exception.StorException
        :return: tuple
        """
        app.logger.exception(error.message)
        return jsonify(error.to_public_dict(g.get('transaction_id', ''))
                       ), error.code

    @app.errorhandler(StandardError)
    def handle_python_errors(error):
        """Log whenever a Python builtin error occurs and return an error response.

        Once transaction IDs are supported, will log them.

        :param error: The exception that was caught
        :type error: StandardError
        :return: tuple
        """
        app.logger.exception(error.message)
        message = "An internal server error has occurred. The transaction_id "\
                  "represents the request and may be used for investigation."
        resp = {
            "error_type": "InternalServerError",
            "message": message,
            "transaction_id": g.get('transaction_id', '')
        }
        return jsonify(resp), 500


def create_app():
    app = Flask(__name__)
    attach_loggers(app)
    attach_models(app)
    register_hooks(app)
    if settings.get('server_debug'):
        app.debug = True
    else:
        register_errorhandlers(app)

    app.secret_key = settings.get('secret_key')

    register_blueprints(app)

    return app
