# from http://stackoverflow.com/a/1695250
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


class IIIFPresentationResource(dict):
    __version__ = '2.0.0'

    descriptive_properties = ['label', 'metadata', 'description', 'thumbnail']
    rights_properties = ['attribution', 'logo', 'license']
    technical_properties = ['@id', '@type', 'format', 'height', 'width',
                            'viewingDirection', 'viewingHing']
    linking_properties = ['related', 'service', 'seeAlso', 'within',
                          'startCanvas']


class Manifest(IIIFPresentationResource):
    pass


class Sequence(IIIFPresentationResource):
    pass


class Canvas(IIIFPresentationResource):
    pass


class Content(IIIFPresentationResource):
    pass


def _manifest_obj(url_root, canvases, manifest_label, metadata, info):
    manifest = {}
    manifest["@id"] = "{url_root}/manifest".format(url_root=url_root)
    manifest["@type"] = "sc:Manifest"
    manifest["label"] = manifest_label if manifest_label else "No label."
    if metadata:
        manifest["metadata"] = metadata,
    if info:
        for key in info:
            if info[key]:
                manifest[key] = info[key]
    manifest["sequences"] = [_sequence_obj(canvases=canvases, url_root=url_root)]
    return manifest


def _sequence_obj(canvases, url_root):
    sequence = {}
    sequence["@type"] = "sc:Sequence"
    sequence['canvases'] = []
    for idx, canvas in enumerate(canvases):
        sequence['canvases'].append(
            _canvas_obj(
                manifest_url=None, url_root=url_root,
                image_id=canvas.get('image_id', idx),
                image_path=canvas.get('path'),
                label=canvas.get('name', canvas.get('path').split("/")[-1]),
                height=canvas.get('height'),
                width=canvas.get('width'),
                annotations=True if canvas.get('transcriptions') or
                                    canvas.get('comments') else False
            )
        )
    return sequence


def _get_bounds(annotation):  # comment or transcription, probably.
    return annotation.get("bounds", "#xywh=1,1,1,1") \
        if "type" not in annotation.get("bounds", "") \
        else "#xywh={}:{}{}{}{}".format(
            annotation['bounds']['type'],
            annotation['bounds']['x'],
            annotation['bounds']['y'],
            annotation['bounds']['w'],
            annotation['bounds']['h']
        )


def _annotation_list_obj(annotation_list_url, canvas_url,
                         transcriptions, comments):  # allow more things?
    annotation_list = {}
    annotation_list['@id'] = annotation_list_url
    annotation_list['@type'] = "sc:AnnotationList"
    annotation_list['resources'] = [
        {
            "@type": "oa:Annotation",
            "motivation": "sc:painting",
            "resource": {"@type": "cnt:ContentAsText",
                         "chars": transcription['text'],
                         "format": "text/plain",
                         "language": transcription['language_code']},
            "on": "{}{}".format(canvas_url, _get_bounds(transcription))
        }
        for transcription in transcriptions
    ] + [
        {
            "@type": "oa:Annotation",
            "motivation": "sc:commenting",
            "resource": {"@type": "dctypes:Text",
                         "chars": comment['text'],
                         "format": "text/plain"},
            "on": "{}{}".format(canvas_url, _get_bounds(comment))
        }
        for comment in comments
    ]
    return annotation_list


def _canvas_obj(manifest_url,
                url_root,
                image_id,
                image_path,
                label,
                height,
                width,
                annotations=None
                ):
    if manifest_url:
        canvas_id = iiif_metadata_url(manifest_url, image_id, 'canvas')
    elif url_root:
        canvas_id = "{root_url}/canvas/{canvas_name}".format(
            root_url=url_root, canvas_name=image_id
        )
    else:
        raise ValueError("must provide one of manifest_url or url_root")
    resource_url = "{}/full/full/0/native.jpg".format(image_path)
    image_anno_url = iiif_metadata_url(manifest_url, image_id, 'annotation')
    resource = {
        "@id": resource_url,
        "@type": "dctypes:Image",
        "format": "image/jpeg",
        "height": height,
        "width": width,
        "service": {
             "@id": image_path
        }
    }
    image = {
        "@id": image_anno_url,
        "@type": "oa:Annotation",
        "motivation": "sc:painting",
        "resource": resource,
        "on": canvas_id
    }
    canvas = {
        "@id": canvas_id,
        "@type": "sc:Canvas",
        "label": label,
        "height": height,
        "width": width,
        "images": [image]
    }
    if annotations:
        anno_list_url = iiif_metadata_url(manifest_url,
                                          image_id, 'list')
        anno_list = [{"@id": anno_list_url,
                      "@type": "sc:AnnotationList"}]
        canvas['otherContent'] = anno_list
    return canvas
