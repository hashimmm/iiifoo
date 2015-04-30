from urllib import unquote

from flask import render_template, redirect, url_for, request

from . import viewing
from dbmodels import Manifest
from manifest_ops import iiif_metadata_url
from source_mappings import source_mapping, is_dynamic_source
from iiifoo_utils import dict_to_rest_options, list_to_rest_options


def _path_cat_map(manifests):
    manifest_paths = [
        unquote(url_for('.get_manifest', source_type=item.source_type,
                options=list_to_rest_options([
                    item.source_url,
                    item.id
                ])))
        for item in manifests
    ]
    manifest_categories = [item.manifest_category for item in manifests]
    return zip(manifest_paths, manifest_categories)


@viewing.route('/')
def home():
    manifests = Manifest.query.all()
    authored_item_manifests = _path_cat_map(manifests)
    return render_template('mirador2_index.html',
                           uris_and_locations=authored_item_manifests)


# We could have source type logins like this:
# @viewing.route('/<source_type>/login')
# def log_in(source_type):
#     params = request.form
#     ph = source_mapping[source_type]
#     ph = ph(params)
#     ph.login()
# def source_login_required(func):
#     def new_func(*args, **kwargs):
#         user = request.form.get('userid', None) or request.args.get('userid',
#                                                                     None)
#         req_source_type = kwargs.get('source_type', None)
#         session_source_type = session.get('source_type')
#         if user == session.get('foobar', False):
#             pass
#         func(*args, **kwargs)
# def _current_user(source_type, source_url):
#     return g.get((source_type, source_url))


# Routes to ensure the viewer paths work.
# TODO: check if we need all of them.
@viewing.route('/viewer/images/<path:img>', methods=['GET'])
def get_img(img):
    """Retrieve files for the mirador app."""
    return redirect(url_for('static', filename='mirador/images/' + img))
@viewing.route('/viewer/css/<path:img>', methods=['GET'])
def get_css(img):
    """Retrieve files for the mirador app."""
    return redirect(url_for('static', filename='mirador/css/' + img))
@viewing.route('/viewer/fonts/<path:img>', methods=['GET'])
def get_fonts(img):
    """Retrieve files for the mirador app."""
    return redirect(url_for('static', filename='mirador/fonts/' + img))
@viewing.route('/viewer/themes/<path:img>', methods=['GET'])
def get_themes(img):
    """Retrieve files for the mirador app."""
    return redirect(url_for('static', filename='mirador/themes/' + img))
@viewing.route('/viewer/mirador.js', methods=['GET'])
def get_mirador_js():
    """Retrieve files for the mirador app."""
    return redirect(url_for('static', filename='mirador/mirador.js'))
@viewing.route('/viewer/ZeroClipboard.swf', methods=['GET'])
def get_some_swf():
    """Retrieve files for the mirador app."""
    return redirect(url_for('static', filename='mirador/ZeroClipboard.swf'))


# TODO: enable returning an embeddable viewer on POST.
@viewing.route('/viewer/<source_type>', methods=['GET', 'POST'])
def specific_manifest(source_type):
    if request.method == 'POST':
        params = request.get_json()
    else:
        params = request.args
    try:
        ph = source_mapping[(source_type, 'view')]
    except KeyError:
        try:
            ph = source_mapping[(source_type, 'base')]
        except KeyError:
            return "not found", 404
    if not is_dynamic_source(ph):
        ph = ph(params)
        source_url = ph.source_url
        # auth_service = ph.auth_service(source_url)
        canvas_id = ph.canvas_id
        url = url_for('.get_manifest', source_type=source_type,
                      options=list_to_rest_options([
                          source_url,
                          ph.manifest_identifier
                          ])
                      )
        if canvas_id:
            canvas_id = iiif_metadata_url(url, canvas_id, 'canvas')

        # category = manifest.manifest_category
        manifests = Manifest.query.filter_by(
            source_url=source_url,
            source_type=source_type
        )
        manifests = _path_cat_map(manifests)
        response = render_template(
            'mirador2_index.html',  # auth=auth_service,
            uris_and_locations=manifests,
            preloaded_manifest=url,
            do_not_save=True
        ) if not canvas_id else render_template(
            'mirador2_index.html',  # auth=auth_service,
            uris_and_locations=manifests,
            preloaded_manifest=url,
            preloaded_image=canvas_id,
            do_not_save=True
        )
        return response
    else:
        ph = ph(params)
        category = ph.category
        manifest = url_for('.get_manifest', source_type=source_type,
                           options=dict_to_rest_options(request.args))
        return render_template('mirador2_index.html',
                               uris_and_locations=[(manifest, category)],
                               do_not_save=True,
                               preloaded_manifest=manifest)
