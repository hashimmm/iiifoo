"""Various utility methods to aid testing."""


class AlwaysEqual(object):

    """Returns True for any equality comparison."""

    def __eq__(self, value):
        """Test for equality."""
        return True
