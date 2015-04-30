from behave import *
import simplejson
from testutils.manifest_validator import *
from iiifoo_utils import image_id_from_canvas_id


# TODO: Replace response.data with response.get_data()
# as described here: https://github.com/mitsuhiko/werkzeug/blob/
# master/werkzeug/wrappers.py#L869


@given('image info for {no_of_images} image(s)')
def step_impl(context, no_of_images):
    context.no_of_images = int(no_of_images)
    context.authoring_details = simplejson.loads(context.text)


@given('a new manifest is specified')
def step_impl(context):
    context.no_of_existing_images = 0


@given('an existing manifest with {no_of_images} images is specified')
def step_impl(context, no_of_images):
    context.no_of_existing_images = int(no_of_images)


@given('deletion info for {all_or_some} images')
def step_impl(context, all_or_some):
    context.deletion_info = simplejson.loads(context.text)
    context.delete_all = True if all_or_some == 'all' else False


@when('these details are exported')
def step_impl(context):
    assert context.app.post('author/test',
                            data=simplejson.dumps(context.authoring_details),
                            content_type='application/json').status_code == 200


@when('deletion is attempted')
def step_impl(context):
    assert context.app.post('author/test',
                            data=simplejson.dumps(context.deletion_info),
                            content_type='application/json').status_code == 200


@then(u'manifest should reflect updated details')
def step_impl(context):
    manifest_path = '/iiif/test/%s/%s/manifest' \
                    % (context.authoring_details['source_url'],
                       context.authoring_details['manifest_identifier'])

    response = context.app.get(manifest_path)
    assert response.status_code == 200, "Failed to retrieve manifest" \
                                        " at path %s" % manifest_path
    manifest_str = response.data
    manifest_json = simplejson.loads(manifest_str)
    ensure_manifest_schema_conformance(manifest_json)
    check_updated_details(manifest_json, context.authoring_details)


# the following needs to be split into multiple steps :/
@then('a valid manifest should exist with this info')
def step_impl(context):
    manifest_path = '/iiif/test/%s/%s/manifest' % \
                    (context.authoring_details['source_url'],
                     context.authoring_details['manifest_identifier'])

    response = context.app.get(manifest_path)
    assert response.status_code == 200, "Failed to retrieve manifest" \
                                        " at path %s" % manifest_path
    manifest_str = response.data
    context.manifest_json = simplejson.loads(manifest_str)
    ensure_manifest_schema_conformance(context.manifest_json)
    ensure_manifest_details_integrity(context.authoring_details,
                                      context.manifest_json,
                                      context.no_of_existing_images)


# noinspection PyUnusedLocal
@then(u'image info should be appended to existing manifest')
def step_impl(context):
    pass  # The next step does the validation already for the append case too


@then('only this image should be deleted from manifest')
def step_impl(context):
    manifest_id = context.deletion_info['manifest_identifier']
    manifest_path = '/iiif/test/%s/%s/manifest' % \
                    (context.deletion_info['source_url'],
                     manifest_id)
    response = context.app.get(manifest_path)
    assert response.status_code == 200, "Failed to retrieve manifest" \
                                        " at path %s" % manifest_path
    manifest_str = response.data
    manifest_json = simplejson.loads(manifest_str)
    canvases = manifest_json['sequences'][0]['canvases']
    canvas_image_ids = [image_id_from_canvas_id(canvas['@id'])
                        for canvas in canvases]
    assert context.deletion_info['images'][0]['image_id'] not \
        in canvas_image_ids, "Image not deleted"


@then('manifest itself should be deleted')
def step_impl(context):
    manifest_id = context.deletion_info['manifest_identifier']
    manifest_path = '/iiif/test/%s/%s/manifest' % \
                    (context.deletion_info['source_url'],
                     manifest_id)
    response = context.app.get(manifest_path)
    assert response.status_code == 404


@then('manifest should contain an annotation link for each annotated image')
def step_impl(context):
    canvases = context.manifest_json['sequences'][0]['canvases']
    annotated_canvases = canvases[-context.no_of_images:]
    for annotated_canvas in annotated_canvases:
        annotation_link = annotated_canvas.get(
            'otherContent', [{}]
        )[0].get("@id")

        assert annotation_link, "Annotation list link not found in " \
                                "annotated image %s" % annotated_canvas


@then('annotations must be present in respective annotation lists')
def step_impl(context):
    canvases = context.manifest_json['sequences'][0]['canvases']
    annotated_canvases = canvases[-context.no_of_images:]
    for index, annotated_canvas in enumerate(annotated_canvases):
        canvas_id = annotated_canvas['@id']
        image_id = image_id_from_canvas_id(canvas_id)
        anno_list_uri = '/iiif/test/%s/%s/list/%s' % \
                        (context.authoring_details['source_url'],
                         context.authoring_details['manifest_identifier'],
                         image_id)

        response = context.app.get(anno_list_uri)
        assert response.status_code == 200, "Failed to retrieve annotation " \
                                            "list at path %s" % anno_list_uri
        anno_str = response.data
        anno_json = simplejson.loads(anno_str)
        check_annotations_in_list(anno_json,
                                  context.authoring_details['images'][index])
