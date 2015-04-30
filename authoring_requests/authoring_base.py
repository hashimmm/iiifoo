import logging
from dbmodels import Manifest


fh = logging.FileHandler('authoring_requests.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]',
    datefmt='%d/%m/%Y %I:%M:%S %p'
))

logger = logging.getLogger("authoring_requests")
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)


class AuthoringRequestBase(object):
    """ To enable custom handling of any sort of manifest-related requests,
    subclass and provide a `type_name`, and add it to
    `authoring_requests.source_mapping` as `(type_name, 'base')`.

    `type_name` is the unique identifier for a particular request handler base.

    Manifest creation requests are called "export" requests,
    and there are "view" and "delete" requests as well. For each, there is a
    corresponding interface, and implementing the interface keeping the
    `type_name` same will enable those requests for the type.
    """
    type_name = None
    discoverable = NotImplemented
    """Allow/disallow the request type to be discoverable via sitemaps."""

    def __init__(self, params):
        logger.debug("got params: ")
        logger.debug(params)

    @classmethod
    def get_all_manifest_path_components(cls):
        """Get all the source_url/id pairs for manifests from a source type.

        They are combined with the type_name and other URIs to form paths to
        allow discovery from the sitemap.

        :returns: list - dicts containing values for source_url and manifest id.
            Return value must always correspond to the manifest view function's
            arguments, minus the source_type.
        """
        manifests = Manifest.query.filter_by(source_type=cls.type_name).all()
        return [{'source_url': m.source_url,
                 'manifest_id': m.id} for m in manifests]

    @property
    def manifest_identifier(self):
        """ Manifest identifier (has to be unique).
        """
        raise NotImplementedError()

    @property
    def source_url(self):
        """ The url associated with the source.
        Used primarily for differentiating between different instances
        of the same image source to avoid conflicts.
        Blank will not work fine. If such situations are not expected,
        use some string like N/A.
        """
        raise NotImplementedError()

    @property
    def user(self):
        """ The user w.r.t. the source type associated with with the
         current request. Has to be an integer.
        """
        raise NotImplementedError()

    @classmethod
    def is_allowed(cls, image_id, cookie):
        """ Check if the user indicated by `cookie` is allowed to view 
        the image. Return viewable manifests. 
        (This means that if permissions aren't needed just return 
        True.)
        """
        return NotImplementedError()
