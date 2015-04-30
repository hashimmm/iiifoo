"""Mixins to help implement authoring sources.

__init__ is always called with request json data;
but viewing may be requested as GET as well in which case it will
be called with request query parameters.
"""


class ExportRequestInterface(object):
    """ Subclass this to provide exporting..

    "Exporting" means creating/editing a manifest and adding information
    about images to it. This information is stored in a database.

    Methods are called without arguments to allow for flexibility.
    Simply initialize whats needed within the __init__ method.
    """

    @property
    def images(self):
        """ List of objects,
        each containing a `name`, `width`, `height`, `path`, `image_id`
        and, optionally, `transcriptions` and/or `comments`.

        `transcriptions` must be a list of objects containing
        values for "language_code" and "text" and `comments`
        must be a list of objects containing "text": value.
        """
        raise NotImplementedError()

    @property
    def manifest_label(self):
        """ Manifest label.
        """
        raise NotImplementedError()

    @property
    def metadata(self):
        """ Manifest metadata. Should be a list containing
        items like {"label": "foo", "value": "bar"}
        """
        raise NotImplementedError()

    @property
    def manifest_category(self):
        """ The category under which to organize the manifest.
        Used in the Mirador UI.
        """
        raise NotImplementedError()

    @property
    def info(self):
        """ Return a dict. Key-value pairs of this dict are
        entered into the manifest root as is. The Mirador UI displays
        the following metadata info from the manifest root:
            "description",
            "agent",
            "location",
            "date",
            "attribution",
            "license",
            "see_also",
            "service",
            "within"
        so having these fields in the dict will be helpful.
        """
        raise NotImplementedError()


class ViewRequestInterface(object):

    @property
    def canvas_id(self):
        """Called when viewing is attempted; return the required canvas ID.
        Return blank if no image should be opened in the viewer.
        This only needs be the canvas identifier, and not the entire URL,
        since in this authoring scheme, the entire URL is constructed by the
        application.
        """
        raise NotImplementedError()


class DeleteRequestInterface(object):

    @property
    def images(self):
        """ List of objects,
        each containing an `image_id`.
        """
        raise NotImplementedError()
