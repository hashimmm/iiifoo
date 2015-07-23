"""Defines the URLs for authoring manifests."""
import logging
from urllib import unquote

from flask.views import MethodView
from flask import jsonify, request, url_for

from . import authoring
from iiifoo_server import db
import manifest_ops
import iiifoo_utils
from source_mappings import source_mapping, is_dynamic_source
import exception


logger = logging.getLogger('authoring_views')


class AuthoringAPI(MethodView):

    """Authoring actions mapped to HTTP request methods."""

    def get(self, source_type):
        """Get doesn't do anything yet."""
        pass

    def post(self, source_type):
        """Perform any valid action.

        Action is determined by the value of the 'action' key in the request
        body. Request body is expected to be JSON.
        """
        params = request.get_json(force=True, silent=True) or request.values
        action = params.get('action', 'export').lower()
        if not action or action == 'export':
            resp = self._export_image(params, source_type)
        elif action == 'delete':
            resp = self._delete_image(params, source_type)
        else:
            resp = "bad action %s" % action, 502
            logger.info("Invalid request received! Bad action \"%s\"" %
                        action)
        logger.info('Export response:')
        logger.info(resp)
        return resp

    def delete(self, source_type):
        """Delete an image for the given source type.

        Options specified in request body (which has to be JSON).
        """
        params = request.get_json(force=True, silent=True) or request.values
        return self._delete_image(params, source_type)

    def put(self, source_type):
        """Add an image for the given source type.

        Options specified in request body (which has to be JSON).
        """
        params = request.get_json(force=True, silent=True) or request.values
        return self._export_image(params, source_type)

    @staticmethod
    def _export_image(params, source_type):
        ph = source_mapping[(source_type, 'export')]
        if is_dynamic_source(ph):
            raise exception.InvalidAPIAccess("This source doesn't "
                                             "support authoring.")
        ph = ph(params)
        images = ph.images
        optpath = iiifoo_utils.list_to_rest_options([ph.source_url,
                                                     ph.manifest_identifier])
        manifest_url = url_for('viewing.get_manifest', source_type=source_type,
                               options=optpath)
        # Because url_for will quote it again, we'll re-unquote it.
        # Alternatively, create a RawPathConverter extending
        # werkzeug.routing.PathConverter and remove the quoting in to_url.
        manifest_url = unquote(manifest_url)
        manifest_url = request.url_root + manifest_url.lstrip('/')
        if images:
            manifest_ops.add(db.session,
                             ph.manifest_identifier, source_type, ph.source_url,
                             ph.manifest_label, ph.manifest_category,
                             ph.metadata, manifest_url, images,
                             ph.user, ph.info,
                             commit=True)
            logger.info("Exporting request processed, "
                        "manifest generated.")
            resp = jsonify({"status": "exported", "success": True,
                            "message": "exported %s image(s)" % len(images)})
        else:
            resp = jsonify({"status": "did nothing", "message":
                            "no exportable images found.", "success": False})
            logger.info("No exportable images found!")
        return resp

    @staticmethod
    def _delete_image(params, source_type):
        ph = source_mapping[(source_type, 'delete')]
        if is_dynamic_source(ph):
            raise exception.InvalidAPIAccess("This source doesn't "
                                             "support authoring.")
        ph = ph(params)
        manifest_ops.delete(session=db.session,
                            image_ids=ph.images,
                            manifest_id=ph.manifest_identifier,
                            source_url=ph.source_url, source_type=source_type,
                            user=ph.user, commit=True)
        resp = jsonify({"success": True, "message": "deleted"})
        logger.info("Images deleted!")
        return resp


authoring_view = AuthoringAPI.as_view('author')

authoring.add_url_rule('/author/<source_type>',
                       view_func=authoring_view,
                       methods=['GET', 'DELETE'])

authoring.add_url_rule('/author/<source_type>',
                       view_func=authoring_view,
                       methods=['POST', 'PUT'])
