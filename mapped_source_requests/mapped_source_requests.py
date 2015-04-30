from mapping_interfaces import MappedSourceRequestBase


class VanillaDynamicView(MappedSourceRequestBase):

    type_name = 'test'
    discoverable = False

    def manifest_label(self):
        return super(VanillaDynamicView, self).manifest_label()

    def __init__(self, options):
        super(VanillaDynamicView, self).__init__(options)

    def category(self):
        return super(VanillaDynamicView, self).category()

    def annotation_params(self, canvas_name):
        return super(VanillaDynamicView, self).annotation_params(canvas_name)

    def manifest_params(self):
        return super(VanillaDynamicView, self).manifest()
