import simplejson
from flask import jsonify, request, url_for

from . import viewing
import iiifoo_utils
from dbmodels import Manifest, Image
from source_mappings import source_mapping, is_dynamic_source


pub_req_optmap = ['source_url', 'manifest_id']


# Make sure to change relevant paths in tests etc. if/when this changes.
@viewing.route('/iiif/<source_type>/<path:options>/manifest')
@iiifoo_utils.crossdomain(origin="*")
@iiifoo_utils.iiif_presentation_api_view
def get_manifest(source_type, options):
    """Get a manifest for the given info.

    For authoring sources, gets it from db.

    For dynamic sources, creates it on request.
    """
    source_type = source_mapping.get((source_type, 'base'))
    if not source_type:
        return jsonify({"message": "bad type", "success": False}), 502
    if not is_dynamic_source(source_type):
        options = iiifoo_utils.parse_mapped_rest_options(options, pub_req_optmap)
        if not source_type:
            return jsonify({"message": "bad type", "success": False}), 502
        manifest = Manifest.query.filter_by(
            id=options['manifest_id'], source_type=source_type.type_name,
            source_url=options['source_url']
        ).first()
        if not manifest:
            return jsonify({"message": "manifest not found",
                            "success": False}), 404
        # canvases = manifest['sequences'][0]['canvases']
        # canvas_image_ids = [image_id_from_canvas_id(canvas['@id'])
        #                     for canvas in canvases]
        # for image_id in canvas_image_ids:
        #     if source_type.allowed_access(image_id=image_id,
        #                                   cookie=session[''])  # TODO
        responsetext = manifest.manifest
    else:
        parsed_options = iiifoo_utils.parse_rest_options(options)
        nph = source_type(parsed_options)
        responsetext = \
            nph.get_manifest(url_root=request.base_url.rstrip("manifest"))
    return responsetext, 200


@viewing.route('/iiif/<source_type>/<path:options>'
               '/list/<canvas_name>')
@iiifoo_utils.crossdomain(origin="*")
@iiifoo_utils.iiif_presentation_api_view
def get_annotation_list(source_type, options, canvas_name):
    source_type = source_mapping.get((source_type, 'base'))
    if not source_type:
        return jsonify({"message": "bad type", "success": False}), 502
    if not is_dynamic_source(source_type):
        options = iiifoo_utils.parse_mapped_rest_options(options, pub_req_optmap)
        pi = Image.query.filter_by(
            identifier=canvas_name,
            manifest_id=options['manifest_id'],
            source_type=source_type.type_name,
            source_url=options['source_url']
        ).first()
        if pi:
            response = jsonify(simplejson.loads(pi.annotations)), 200
        else:
            response = jsonify({"message": "image not found",
                                "success": False}), 404
        return response
    else:
        options = iiifoo_utils.parse_rest_options(options)
        nph = source_type(options)
        manifest_url = url_for('.get_manifest', source_type=source_type,
                               options=options)
        manifest_url = "".join([request.url_root.rstrip('/'), manifest_url])
        annotations = nph.get_annotations(canvas_name=canvas_name,
                                          manifest_url=manifest_url)
        return jsonify(annotations)


@viewing.route('/iiif/<source_type>/<path:options>/canvas/<canvas_name>')
@iiifoo_utils.crossdomain(origin="*")
@iiifoo_utils.iiif_presentation_api_view
def get_canvas(source_type, options, canvas_name):
    source_type = source_mapping.get((source_type, 'base'))
    if not source_type:
        return jsonify({"message": "bad type", "success": False}), 502
    if not is_dynamic_source(source_type):
        options = iiifoo_utils.parse_mapped_rest_options(options, pub_req_optmap)
        m = Manifest.query.filter_by(
            id=options['manifest_id'],
            source_type=source_type.type_name,
            source_url=options['source_url']
        ).first()
        if not m:
            return jsonify({"message": "manifest not found",
                            "success": False}), 404
        manifest = simplejson.loads(m.manifest)
        canvases = manifest['sequences'][0]['canvases']
        canvas_image_ids = [iiifoo_utils.image_id_from_canvas_id(canvas['@id'])
                            for canvas in canvases]
        index = canvas_image_ids.index(canvas_name)
        response = jsonify(canvases[index]), 200
        return response
    else:
        raise NotImplementedError()
