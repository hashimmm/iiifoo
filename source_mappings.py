import inspect
from mapped_source_requests import mapping_interfaces
from authoring_requests import authoring_api_mixins, authoring_base
from authoring_requests.authoring_requests import (
    VanillaBase, VanillaDeleteRequest, VanillaExportRequest,
    StandardAuthoringAPIv1, StandardAuthoringAPIv1Base
)
from mapped_source_requests.mapping_interfaces import \
    MappedSourceRequestBase
import source_type_plugins
from source_type_plugins import *
# DO NOT REMOVE THE ABOVE IMPORT, IT IS NOT UNUSED.

plugins = []


for item in source_type_plugins.__all__:
    if item.startswith('__') and item.endswith('__'):
        continue
    plugins.append({k: v for k, v in locals()[item].__dict__.items()
                    if not (k.startswith('__') and k.endswith('__'))})


source_mapping = {
    ('test', 'base'): VanillaBase,
    ('test', 'export'): VanillaExportRequest,
    ('test', 'delete'): VanillaDeleteRequest,
    ('api_v0_1a', 'base'): StandardAuthoringAPIv1Base,
    ('api_v0_1a', 'export'): StandardAuthoringAPIv1,
}


def _req_type(obj):
    t = None
    if not inspect.isclass(obj):
        pass
    elif issubclass(obj, authoring_api_mixins.ViewRequestInterface):
        t = 'view'
    elif issubclass(obj, authoring_api_mixins.DeleteRequestInterface):
        t = 'delete'
    elif issubclass(obj, authoring_api_mixins.ExportRequestInterface):
        t = 'export'
    elif issubclass(obj, authoring_base.AuthoringRequestBase)\
            or issubclass(obj, mapping_interfaces.MappedSourceRequestBase):
        t = 'base'
    return t


for objects in plugins:
    for obj in objects:
        is_request = _req_type(objects[obj])
        if is_request:
            source_mapping[(objects[obj].type_name, is_request)] = objects[obj]


def is_dynamic_source(cls):
    return issubclass(cls, MappedSourceRequestBase)


def is_dynamic_source_object(obj):
    return issubclass(obj.__class__, MappedSourceRequestBase)
