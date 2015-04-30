from datetime import datetime

import simplejson
from flask import render_template, url_for, request, Response, current_app

from . import discovery
from source_mappings import source_mapping


manifest_view_name = "viewing.get_manifest"


@discovery.route('/sitemap_index.xml')
def sitemap_index():
    sources = []
    for source in source_mapping:
        if source[1] == 'base' and source_mapping[source].discoverable:
            sources.append(source_mapping[source].type_name)
    root_url = request.url_root.rstrip('/')
    urls = [
        "{}{}".format(
            root_url,
            url_for('.source_sitemap',
                    source_type=source_type)
        )
        for source_type in sources
    ]
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_urls = [(url, today) for url in urls]
    return Response(render_template('sitemap_index.xml',
                                    sitemap_urls=sitemap_urls),
                    mimetype='text/xml')


@discovery.route('/sitemap/<source_type>/sitemap.xml')
def source_sitemap(source_type):
    components = source_mapping[(source_type, 'base')]\
        .get_all_manifest_path_components()
    root_url = request.url_root.rstrip('/')
    urls = [
        "{}{}".format(
            root_url,
            url_for(manifest_view_name, source_type=source_type, **component)
        )
        for component in components
    ]
    # image_urls = [
    #     _iiif_urls_from_manifest(simplejson.loads(
    #         current_app.view_functions[view](source_type=source_type,
    #                                          **component).data
    #     ))
    #     for component in components
    # ]
    # urls = zip(urls, image_urls)
    urls = zip(urls, [[] for _ in urls])
    return Response(render_template('sitemap.xml', urls=urls),
                    mimetype='text/xml')


@discovery.route('/iiifmap/<source_type>/iiifmap.xml')
def source_iiifmap(source_type):
    components = source_mapping[(source_type, 'base')]\
        .get_all_manifest_path_components()
    root_url = request.url_root.rstrip('/')
    urls = [
        "{}{}".format(
            root_url,
            url_for(manifest_view_name, source_type=source_type, **component)
        )
        for component in components
    ]
    image_urls = [
        _iiif_urls_from_manifest(_try_manifest(manifest_view_name,
                                               source_type, component))
        for component in components
    ]
    urls = zip(urls, image_urls)
    return Response(render_template('iiifmap.xml', urls=urls),
                    mimetype='text/xml')


def _try_manifest(view, source_type, component):
    try:
        m = simplejson.loads(
            current_app.view_functions[view](source_type=source_type,
                                             **component).data
        )
    except Exception as e:
        current_app.logger.exception(e.message)
        m = {}
    return m


def _iiif_urls_from_manifest(manifest):
    sequences = manifest.get('sequences', [])
    urls = []
    for sequence in sequences:
        canvases = sequence.get('canvases', [])
        for canvas in canvases:
            images = canvas.get('images', [])
            for image in images:
                imageurl = (image.get('resource', {})
                                 .get("service", {})
                                 .get("@id"))
                if imageurl:
                    urls.append(imageurl)
    return urls
