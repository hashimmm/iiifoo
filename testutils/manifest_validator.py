from testutils.presentation_api.implementations.manifest_factory.loader import \
    ManifestReader
from iiifoo_utils import image_id_from_canvas_id


def validate(manifestjson, logger=None):
    """Validate a given manifest json object."""
    mr = ManifestReader(manifestjson)
    try:
        r = mr.read()
        js = r.toJSON()
    except Exception as e:
        if logger:
            logger.exception(e)
        print e
        valid = False
    else:
        valid = True
    print mr.get_warnings()
    if logger:
        logger.warn(mr.get_warnings())
    return valid


def assert_equal(first, second):
    assert first == second, \
        "%s != %s" % (first, second)


def ensure_manifest_details_integrity(detailsobj, manifest_json, start=0):
    sequences = manifest_json['sequences']
    canvases = sequences[0]['canvases']
    no_of_images = len(detailsobj['images'])
    assert_equal(len(sequences), 1)
    assert_equal(len(canvases), no_of_images + start)
    for i in xrange(start, start+no_of_images):
        assert_equal(canvases[i]['label'],
                     detailsobj['images'][i-start]['name'])
        assert_equal(canvases[i]['width'],
                     detailsobj['images'][i-start]['width'])
        assert_equal(canvases[i]['height'],
                     detailsobj['images'][i-start]['height'])
        image_resource = canvases[i]['images'][0]['resource']
        assert_equal(image_resource['service']['@id'],
                     detailsobj['images'][i-start]['path'])
        assert_equal(image_resource['width'],
                     detailsobj['images'][i-start]['width'])
        assert_equal(image_resource['height'],
                     detailsobj['images'][i-start]['height'])


def ensure_manifest_schema_conformance(manifest_json):
    assert validate(manifest_json), \
        "Manifest json: \n%s\n is invalid" % manifest_json


def check_updated_details(manifest_json, details):
    sequences = manifest_json['sequences']
    canvases = sequences[0]['canvases']
    new_image_ids = [image['image_id'] for image in details['images']]
    updated_canvases = [canvas for canvas in canvases
                        if image_id_from_canvas_id(canvas["@id"])
                        in new_image_ids]
    updated_canvases = {image_id_from_canvas_id(canvas["@id"]): canvas
                        for canvas in updated_canvases}
    assert_equal(manifest_json['label'], details['manifest_label'])
    for image_id in new_image_ids:
        canvas = updated_canvases[image_id]
        image = [image for image in details['images']
                 if image['image_id'] == image_id][0]
        assert_equal(canvas['label'], image['name'])
        assert_equal(canvas['width'], image['width'])
        assert_equal(canvas['height'], image['height'])
        image_resource = canvas['images'][0]['resource']
        assert_equal(image_resource['service']['@id'], image['path'])
        assert_equal(image_resource['width'], image['width'])
        assert_equal(image_resource['height'], image['height'])


def check_annotations_in_list(annotation_list, imageobj):
    resources = annotation_list['resources']
    relevant_resources = []
    for resource in resources:
        if image_id_from_canvas_id(resource['on']) == imageobj['image_id']:
            relevant_resources.append(resource)
    list_comments = [item['resource']['chars'] for item in resources
                     if item['motivation'] == "oa:commenting"]
    list_transcriptions = [item['resource']['chars'] for item in resources
                           if item['resource']['@type'] == "cnt:ContentAsText"]
    for comment in imageobj.get('comments', []):
        assert comment['text'] in list_comments, \
            "Comment %s not found" % comment['text']
    for transcription in imageobj.get('transcriptions', []):
        assert transcription['text'] in list_transcriptions, \
            "Comment %s not found" % transcription['text']
