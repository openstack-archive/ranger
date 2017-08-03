"""test_transaction module."""


import unittest

from audit_server.storage.transaction import Base


class Test(unittest.TestCase):
    """test transaction class."""

    def test_add_record(self):
        """test that add_record throws an NotImplementedError exception."""
        baseConn = Base("test_url")
        self.assertRaises(NotImplementedError, baseConn.add_record,
                          transaction=None)

    def test_get_latest_record(self):
        """test that add_record throws an NotImplementedError exception."""
        baseConn = Base("test_url")
        self.assertRaises(NotImplementedError, baseConn.get_records,
                          query=None)
