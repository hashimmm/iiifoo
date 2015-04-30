class IiifooError(Exception):

    """Base exception for all IIIFOO exceptions."""

    message = "Generic IIIFOO exception"
    code = 500

    def to_dict(self, transaction_id=None):
        """Get a JSON-serializable error representation."""
        obj = {
            "error_type": self.__class__.__name__,
            "message": self.message
        }
        if transaction_id:
            obj['transaction_id'] = transaction_id
        obj.update({key: self.kwargs[key] for key in self.kwargs if key})
        return obj

    def to_public_dict(self, transaction_id=None):
        message = self.public_message if self.public_message else self.message
        obj = {
            "error_type": self.__class__.__name__,
            "message": message
        }
        if transaction_id:
            obj['transaction_id'] = transaction_id
        return obj

    def __str__(self):
        """Get exception string; basically the exception message."""
        return self.message

    def __init__(self, message, public_message=None, **kwargs):
        """Initialize an exception object.

        The first argument is the message.
        """
        Exception.__init__(self, message)
        self.message = message if message else self.message
        self.public_message = public_message
        self.kwargs = kwargs


class ExternalInterfaceError(IiifooError):

    """For when an external interface breaks."""

    code = 500


class NotFoundError(IiifooError):

    """Raised when something that a requested entity is not found."""

    code = 404


class UnauthorizedAccessError(IiifooError):

    """Raised when a user requests something they are not authorized for.

    There's no such thing yet.
    """

    code = 403


class InvalidAPIAccess(IiifooError):
    """Raised when there is something wrong with the API request.

    For example, missing parameters, malformatted parameters.
    """

    code = 400
