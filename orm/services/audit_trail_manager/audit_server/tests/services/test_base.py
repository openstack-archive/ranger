"""test_base module."""


from audit_server.services.base import Error
import unittest


class Test(unittest.TestCase):
    """test base class."""

    def test_init_Error(self):
        """Test that init of Error succeeded."""
        Error("test")
        pass
