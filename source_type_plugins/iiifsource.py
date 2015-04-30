import logging
from werkzeug.utils import cached_property
import iiifoo_utils
from authoring_requests import authoring_base
from authoring_requests import authoring_requests


logger = logging.getLogger("authoring_requests")


class IIIFBase(authoring_base.AuthoringRequestBase):
    type_name = 'iiifsource_v0_1a'
    discoverable = False

    def __init__(self, params):
        super(IIIFBase, self).__init__(params)
        self.params = params

    @property
    def source_url(self):
        return self.params['iiif_image_server_url']

    @property
    def manifest_identifier(self):
        return self.params['manifest_id']

    @property
    def user(self):
        return -1


class IIIFExportRequest(IIIFBase,
                        authoring_requests.ExportRequestInterface):

    @cached_property
    def images(self):
        images = []
        for image in self.params['images']:
            "`name`, `width`, `height`, `path`, `image_id`"
            name, image_id = image['name'], image['id']
            url = "{}/{}".format(
                self.params['iiif_image_server_url'].rstrip('/'), image_id)
            info_url = "{}/info.json".format(url)
            info = iiifoo_utils.http_request('GET', info_url, get_json=True)
            images.append({
                'image_id': image_id, 'path': url, 'width': info['width'],
                'height': info['height'], 'name': name
            })
        return images

    @cached_property
    def manifest_category(self):
        return self.params.get('manifest_category', 'Generic IIIF source')

    @cached_property
    def manifest_label(self):
        return self.params.get(
            'manifest_label', self.params['manifest_id'])

    @cached_property
    def metadata(self):
        return self.params.get('metadata', [])

    def _extract_meta(self, name):
        val = self.params.get(name, '') or self.params.get(name.lower(), '') \
            or self.params.get(name.upper(), '')
        if not val:
            for item in self.metadata:
                if item.get('label', '').lower() == name.lower():
                    val = item.get('value', '')
                    break
        return val

    @property
    def info(self):
        return {
            "description": self._extract_meta('description'),
            "agent": self._extract_meta('agent'),
            "location": self._extract_meta('location'),
            "date": self._extract_meta('date'),
            "attribution": self._extract_meta('attribution'),
            "license": self._extract_meta('license'),
            "see_also": self._extract_meta('seeAlso')
            or self._extract_meta('see_also'),
            "service": self._extract_meta('service'),
            "within": self._extract_meta('within')
        }

    @property
    def user(self):
        return -1


class IIIFDeleteRequest(IIIFBase, authoring_requests.DeleteRequestInterface):

    @cached_property
    def images(self):
        return self.params['images']


class IIIFViewRequest(IIIFBase, authoring_requests.ViewRequestInterface):

    @property
    def canvas_id(self):
        return ""
