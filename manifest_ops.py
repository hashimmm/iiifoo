import os
import logging

import simplejson
from dbmodels import Manifest, Image
from iiifoo_utils import (
    image_id_from_canvas_id, get_context_and_profile_for_iiif_url
)


fh = logging.FileHandler('manifest_ops.log')
fh.setLevel(logging.DEBUG)
logger = logging.getLogger('manifest_ops')
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)


def _manifest_obj(url_root, canvases, manifest_label, metadata, info,
                  thumbnail_url):
    manifest = {}
    manifest["@id"] = "{url_root}/manifest".format(url_root=url_root)
    manifest["@type"] = "sc:Manifest"
    manifest["label"] = manifest_label if manifest_label else "No label"
    if thumbnail_url:
        manifest["thumbnail"] = thumbnail_url
    if metadata:
        manifest["metadata"] = metadata,
    if info:
        for key in info:
            if info[key]:
                manifest[key] = info[key]
    manifest["sequences"] = [
        _sequence_obj(canvases=canvases, url_root=url_root)]
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
           "resource": {
               "@type": "cnt:ContentAsText",
               "chars": transcription['text'],
               "format": "text/plain",
               "language": transcription[
                   'language_code']},
           "on": "{}{}".format(canvas_url, _get_bounds(transcription))
       }
       for transcription in transcriptions
    ] + [
       {
           "@type": "oa:Annotation",
           "motivation": "oa:commenting",
           "resource": {"@type": "dctypes:Text",
                        "chars": comment[
                            'text'],
                        "format": "text/plain"},
           "on": "{}{}".format(canvas_url,
                               _get_bounds(
                                   comment))
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
        image_anno_url = iiif_metadata_url(manifest_url, image_id, 'annotation')
    elif url_root:
        canvas_id = "{root_url}/canvas/{canvas_name}".format(
            root_url=url_root, canvas_name=image_id
        )
        image_anno_url = canvas_id.replace('/canvas/', '/annotation/')
    else:
        raise ValueError("must provide one of manifest_url or url_root")
    context_and_profile = get_context_and_profile_for_iiif_url(image_path)
    if "http://iiif.io/api/image/2/context.json" ==\
            context_and_profile.get("@context"):
        resource_url = "{}/full/full/0/default.jpg".format(image_path)
    else:
        resource_url = "{}/full/full/0/native.jpg".format(image_path)
    resource = {
        "@id": resource_url,
        "@type": "dctypes:Image",
        "format": "image/jpeg",
        "height": height,
        "width": width,
        "service": {
            "@id": image_path,
            "@context": context_and_profile.get("@context"),
            "profile": context_and_profile.get("profile")
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
        anno_list_url = image_anno_url.replace('/annotation/', '/list/')
        anno_list = [{"@id": anno_list_url,
                      "@type": "sc:AnnotationList"}]
        canvas['otherContent'] = anno_list
    return canvas


def iiif_metadata_url(manifest_url, image_id,
                      resource_type, content_format=None):
    """Get the IIIF metadata resource URI for the image.

    (Given image_id contained in manifest specified
    by manifest_url.)

    Resource types are specified at the following URL:
    http://www.shared-canvas.org/datamodel/iiif/metadata-api.html
    (in the Summary of URI Patterns section).
    """
    collection_metadata_root = iiif_metadata_root(manifest_url)
    resource_type = resource_type.lower()
    if resource_type == 'annotationlist':
        resource_type = 'list'
    if resource_type == 'content':
        path = os.path.join(collection_metadata_root,
                            resource_type, '%s.%s' % (image_id, content_format))
    else:
        path = os.path.join(collection_metadata_root,
                            resource_type, '%s' % image_id)
    return path


def iiif_metadata_root(manifest_url):
    return os.path.dirname(manifest_url)


def delete(session, image_ids, manifest_id, source_type, source_url,
           user, commit=False):
    """ Use session to delete images from manifest with id manifest_id
    with given source_type and source_url.
    """
    image_ids = [str(image['image_id']) for image in image_ids]
    pi = Image.query\
        .filter(Image.identifier.in_(image_ids))\
        .filter(Image.source_type == source_type)\
        .filter(Image.source_url == source_url)\
        .filter(Image.manifest_id == manifest_id).first()
    if pi:
        logger.info("Deleting images :{}".format(image_ids))
        session.delete(pi)
        manifest = Manifest.query.filter_by(id=manifest_id,
                                            source_type=source_type,
                                            source_url=source_url).first()
        if manifest:
            manifest_str = manifest.manifest
            manifest_json = simplejson.loads(manifest_str)
            canvases = manifest_json['sequences'][0]['canvases']
            canvas_image_ids = [image_id_from_canvas_id(canvas['@id'])
                                for canvas in canvases]
            for image_id in image_ids:
                try:
                    index = canvas_image_ids.index(image_id)
                    logger.debug("found index %s" % index)
                    if len(canvases) > 1:
                        canvases.pop(index)
                        manifest.manifest = simplejson.dumps(manifest_json)
                    else:
                        logger.info("deleting manifest")
                        session.delete(manifest)
                        break
                except ValueError:
                    logger.warning("couldn't find index of canvas")
    else:
        logger.info("Couldn't find images {}, so cannot delete."
                    .format(image_ids))
    if commit:
        session.commit()


def create_manifest(url_root, assets, manifest_label, metadata, info,
                    thumbnail_url, return_as='json'):
    """Create a manifest for images with the given info.

    See `add` for more detailed info about the params.

        :param url_root: The URL at which the manifest is supposed to be found.
    :param assets: A list of dict-like objects containing image info.
        Required keys include: 'width', 'height', 'path'.
        Very strongly recommended: 'image_id' (should be unique), 'name'
        Also supported: 'transcriptions', 'comments'.
        Note: `transcriptions` and `comments` are only checked for truthiness as
            far as manifest generation within this method is concerned.
            Determines whether a link to an annotationlist will be inserted
            for the image or not.
    :param manifest_label: The label for the manifest.
    :param metadata: key/value pairs, containing metadata about the manifest.
        Basically, custom metadata fields.
    :param info: key/value pairs, containing information about the manifest.
        Basically, standard-ish metadata fields that clients (like mirador)
        will have a special section for displaying.
    :param return_as: 'json' or 'text'. Determines the type of object returned.
    :return: Manifest. (As dict if return_as is 'json' otherwise as str)
    """
    logger.debug("metadata: {}".format(metadata))
    if metadata:
        serialized_metadata = simplejson.dumps(metadata)
    else:
        serialized_metadata = None
    url_root = url_root.rstrip('/')
    ss = _manifest_obj(url_root=url_root, canvases=assets,
                       manifest_label=manifest_label,
                       metadata=serialized_metadata, info=info,
                       thumbnail_url=thumbnail_url)
    if return_as == 'json':
        manifest = ss
    elif return_as == 'text':
        manifest = simplejson.dumps(ss)
    else:
        raise ValueError("Invalid return_as value. "
                         "Must be one of json or text.")
    return manifest


def _add_images(manifest_url, manifest_json, images):
    for image in images:
        label = image.get('name', os.path.basename(image.get('path')))
        annotations = True if image.get('transcriptions') \
            or image.get('comments') else False
        new_canvas_obj = _canvas_obj(manifest_url=manifest_url,
                                     url_root=None,
                                     image_id=image['image_id'],
                                     width=image['width'],
                                     height=image['height'],
                                     label=label,
                                     image_path=image['path'],
                                     annotations=annotations)
        manifest_json['sequences'][0]['canvases'].append(new_canvas_obj)
    return manifest_json


def create_annotation_list(manifest_url, image, return_as='json'):
    """Create annotation list for image from given parameters.

    :param manifest_url: url of manifest containing the image.
    :param image: dict containing values for the keys:
        "image_id" (str),
        "comments" (list),
        "transcriptions" (list).

        `comments` and `transcriptions` are lists of objects,

        `transcriptions` objects should have a value for the keys:
            "text" (str),
            "language_code" (str),
            "bounds" (str or dict) (optional);
        while objects in `comments` need to have a value for:
            "text",
            "bounds" (optional).

        `bounds` ought to either be a string according to the spatial dimension
        spec found at: http://www.w3.org/TR/media-frags/#naming-space or an
        object comprised of:
            "type" (str) ("pixel" or "percent"),
            "x" (int),
            "y" (int),
            "w" (int),
            "h" (int).

        Although specifying `bounds` is optional, the default value of bounds
        may be subject to change in subsequent releases. Specifying is better.
    :param return_as: "text" or "json". Specifying "json" will return a pythonic
        representation of a JSON object, the former returns a string.
    """
    if image.get('transcriptions') or image.get('comments'):
        anno_list_url = iiif_metadata_url(manifest_url,
                                          image['image_id'],
                                          'list')
        canvas_url = iiif_metadata_url(manifest_url,
                                       image['image_id'],
                                       'canvas')
        anno_list = _annotation_list_obj(
            annotation_list_url=anno_list_url,
            canvas_url=canvas_url,
            transcriptions=image.get('transcriptions', []),
            comments=image.get('comments', [])
        )
    else:
        anno_list = {}
    if return_as == 'json':
        pass
    elif return_as == 'text':
        anno_list = simplejson.dumps(anno_list)
    else:
        raise ValueError("Invalid return_as value. "
                         "Must be one of json or text.")
    return anno_list


def _delete_images(manifest_json, images):
    canvases = manifest_json['sequences'][0]['canvases']
    image_ids = [str(image['image_id']) for image in images]
    canvases_after_deleting = [canvas for canvas in canvases if
                               image_id_from_canvas_id(canvas['@id'])
                               not in image_ids]
    manifest_json['sequences'][0]['canvases'] = canvases_after_deleting
    return manifest_json


def _update_manifest(manifest, images, manifest_url,
                     manifest_label=None, manifest_category=None, info=None):
    """ Update a given manifest in place using given images.

     Manifest_url is required for adding images.
    Replaces existing images too.
    Also updates manifest_label, manifest_category and info if
    provided.
    """
    manifest_image_ids = [m_image.identifier for m_image
                          in manifest.images]
    manifest_json = simplejson.loads(manifest.manifest)
    existing_images = [image for image in images if image['image_id']
                       in manifest_image_ids]
    manifest_json = _delete_images(manifest_json, existing_images)
    manifest_json = _add_images(manifest_url, manifest_json, images)
    manifest_json['label'] = manifest_label
    if info:
        for key in info:
            if info[key]:
                manifest_json[key] = info[key]
    manifest.label = manifest_label or manifest.label
    manifest.manifest_category = manifest_category or \
        manifest.manifest_category
    manifest.manifest = simplejson.dumps(manifest_json)
    return manifest


def _filter_new_images(manifest, images):
    manifest_image_ids = [m_image.identifier for m_image
                          in manifest.images]
    return [image for image in images if image['image_id'] not
            in manifest_image_ids], \
           [image for image in images if image['image_id']
            in manifest_image_ids]


def add(session,
        manifest_id,
        source_type,
        source_url,
        manifest_label,
        manifest_category,
        metadata,
        manifest_url,
        images,
        user,
        info=None,
        commit=False
        ):
    """ Use session to add images to manifest with id
    manifest_id with given source_type and source_url.

    Arguments:
        session: The sqlalchemy session object to use.
        manifest_id: ID for the manifest to add to. May be new or
            an existing ID.
        source_type: The source that this manifest is being created
            for.
        source_url: The URL of the mentioned source. This is used
            to differentiate between multiple instances of the
            same source_type.
        manifest_label: Label for manifest.
        manifest_category: The category under which this manifest will
            appear in Mirador.
        metadata: A list containing objects with a "label" and
            "value". eg. [{"label":"type","value":"cat"}]
        manifest_url: The url at which this manifest will be available.
        images: List of dicts, each containing a name, width, height,
            path, image_id, and, optionally, transcriptions and/or
            comments.
        user: int - user id. Recommended to use -1 if public.
        info: Optional object containing extra fields to add to
            manifest. The following fields have special meaning for
            Mirador UI:
                "description",
                "agent",
                "location",
                "date",
                "attribution",
                "license",
                "see_also",
                "service",
                "within"
        commit: If True, only then is this "add" operation actually
            committed within session. Defaults to False.

    Returns:
        None
    """
    manifest = Manifest.query.filter_by(id=manifest_id,
                                        source_type=source_type,
                                        source_url=source_url).first()
    if manifest:
        _update_manifest(manifest, images, manifest_url,
                         manifest_label, manifest_category, info)
        new_images, existing_images = _filter_new_images(manifest, images)
        for image in new_images:
            annotations = create_annotation_list(manifest_url, image,
                                                 return_as='text')
            # image_uuid = uuid.uuid4()
            pi = Image(identifier=image['image_id'],
                                source_type=source_type,
                                source_url=source_url,
                                manifest_id=manifest_id, status='done',
                                annotations=annotations)
            session.add(pi)
            logger.info("added image {}".format(image))
        for image in existing_images:
            annotations = create_annotation_list(manifest_url, image,
                                                 return_as='text')
            pi = Image.query.filter_by(
                identifier=image['image_id'],
                source_type=source_type,
                source_url=source_url,
                manifest_id=manifest_id
            ).first()
            pi.annotations = annotations
            logger.info("updated image {}".format(image))
    else:
        url_root = iiif_metadata_root(manifest_url)
        manifest = create_manifest(url_root=url_root, assets=images,
                                   manifest_label=manifest_label,
                                   metadata=metadata, info=info,
                                   thumbnail_url='', return_as='text')
        manifest = Manifest(id=manifest_id, source_type=source_type,
                            source_url=source_url,
                            label=manifest_label,
                            manifest_category=manifest_category,
                            manifest=manifest)
        session.add(manifest)
        for image in images:
            annotations = create_annotation_list(manifest_url, image,
                                                 return_as='text')
            image = Image(identifier=image['image_id'],
                          source_type=source_type,
                          source_url=source_url,
                          manifest_id=manifest_id, status='done',
                          annotations=annotations)
            session.add(image)
            logger.info("added image {}".format(image))
    if commit:
        session.commit()
