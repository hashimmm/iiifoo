from werkzeug.utils import cached_property

from iiifoo_utils import dict_to_rest_options
from manifest_ops import create_manifest, create_annotation_list


class MappedSourceRequestBase(object):

    """Base class for dynamically generated IIIF metadata views.

    Currently, only generating a single manifest per request is supported.
    """
    type_name = NotImplemented
    """Name for this source type."""

    discoverable = NotImplemented
    """Allow/disallow the request type to be discoverable via sitemaps."""

    def __init__(self, options):
        """Initialize mapped source request with options.

        :param options: Dict-like object with information to generate manifest.
            For the mirador view request, options are request URL parameters.
            For the manifest JSON and annotations requests, options are REST
            parameters provided within the URL path.
        """
        pass

    @classmethod
    def discoverable_option_sets(cls):
        """Get combinations of "options" for manifests to allow discovery of.

        Sets of options act as manifest identifiers; i.e., in the one manifest
        per request model currently used, the options from the request combine
        to form a single manifest identifier.

        Usually would be all valid sets of options, so as to enable discovery of
        all sets/collections of images.

        Implement this to allow discovery of collection URLs by search engines.

        :return: dict containing option names and values.
            This is used to construct the manifest URL.
        """
        raise NotImplementedError()

    @classmethod
    def get_all_manifest_path_components(cls):
        """Get all the options url paths for manifests from a source type.

        Returned as a list of dicts containing "options": REST_options_path
        to allow passing to view function.

        They are combined with the type_name and other URIs to form paths to
        allow discovery from the sitemap.

        :returns: list - dicts containing values for source_url and manifest id.
            Return value must always correspond to the manifest view function's
            arguments, minus the source_type.
        """
        return [{"options": dict_to_rest_options(optionset)}
                for optionset in cls.discoverable_option_sets()]

    @cached_property
    def manifest_params(self):
        """Get the manifest creation parameters for this instance.

        These will be passed to :py:meth:`~manifest_ops.create_manifest`

        See also: :py:meth:`~manifest_ops.create_manifest`

        :return: Dict-like object containing:
         "assets": A list of dict-like objects containing image info.
            Required keys include: 'width', 'height', 'path'.
            Very strongly recommended: 'image_id' (should be unique), 'name'
            Also supported: 'transcriptions', 'comments'.
            Note: `transcriptions` and `comments` are only checked for
                truthiness.
                Determines whether a link to an annotationlist will be inserted
                for the image or not.
         "metadata": Arbitrary key-value pairs to include as metadata in the
            manifest.
         "info": Metadata key-value pairs supported by mirador to display in
            the manifest information panel.
         "thumbnail_url": URL to the thumbnail for manifest.
        """
        raise NotImplementedError()

    def get_manifest(self, url_root):
        """Get manifest for this instance.

        :param url_root: The URL this manifest is to be found at, minus the
         'manifest.json' or 'manifest' at the end.
        """
        d = self.manifest_params
        return create_manifest(url_root=url_root, assets=d['assets'],
                               manifest_label=self.manifest_label,
                               metadata=d['metadata'], info=d['info'],
                               thumbnail_url=d.get('thumbnail_url', ''),
                               return_as='text')

    @cached_property
    def category(self):
        """The category this manifest's image collection should appear under."""
        raise NotImplementedError()

    @cached_property
    def manifest_label(self):
        """The label for the manifest."""
        raise NotImplementedError()

    def get_annotation_params(self, canvas_name):
        """Get the annotation list creation parameters for this instance.

        See also: :py:meth:`~manifest_ops.create_annotation_list`

        :param canvas_name: `canvas_name` should be an image identifier from
         among the images for the current request.
        :return: A dict-like object containing:
         image_id" (str),
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
        """
        raise NotImplementedError()

    def get_annotations(self, canvas_name, manifest_url):
        """Get the annotations for a canvas_name for this instance.

        :param canvas_name: The image identifier for which annotations are
         required.
        :param manifest_url: url of manifest containing the image.
        """
        image = self.get_annotation_params(canvas_name=canvas_name)
        return create_annotation_list(return_as="json",
                                      image=image,
                                      manifest_url=manifest_url)
