import logging
from werkzeug.utils import cached_property
from authoring_api_mixins import *
import authoring_base


logger = logging.getLogger("authoring_requests")


class VanillaBase(authoring_base.AuthoringRequestBase):
    type_name = 'test'
    discoverable = False

    def __init__(self, params):
        super(VanillaBase, self).__init__(params)
        self.params = params

    @property
    def source_url(self):
        return self.params['source_url']

    @property
    def manifest_identifier(self):
        return self.params['manifest_identifier']

    @property
    def user(self):
        return self.params['user']


class VanillaExportRequest(VanillaBase, ExportRequestInterface):

    @cached_property
    def images(self):
        return self.params['images']

    @cached_property
    def manifest_category(self):
        return self.params['manifest_category']

    @cached_property
    def manifest_label(self):
        return self.params['manifest_label']

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
        return int(self.params['user'])


class VanillaDeleteRequest(VanillaBase, DeleteRequestInterface):

    @property
    def images(self):
        return self.params['images']


class StandardAuthoringAPIv1Base(VanillaBase):
    type_name = 'api_v0_1a'
    discoverable = False


class StandardAuthoringAPIv1(VanillaExportRequest):
    type_name = 'api_v0_1a'
