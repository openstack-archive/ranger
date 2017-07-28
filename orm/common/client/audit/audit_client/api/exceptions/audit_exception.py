"""audit exception module."""


class AuditException(Exception):
    """AuditException class."""

    def __init__(self, error_msg):
        """init method."""
        Exception.__init__(self, error_msg)
