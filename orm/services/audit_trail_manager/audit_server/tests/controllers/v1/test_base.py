"""test_base module."""


import unittest

from audit_server.controllers.v1.base import (ClientSideError,
                                              EntityNotFoundError,
                                              InputValueError)


class Test(unittest.TestCase):
    """test case class."""

    def test_init_ClientSideError(self):
        """test the init method."""
        expected_msg = "This is an error"
        expected_code = 400
        error = ClientSideError(expected_msg)
        self.assertEqual(error.msg, expected_msg)
        self.assertEqual(error.code, expected_code)

    def test_init_InputValueError(self):
        """test the init method."""
        name = "name1"
        value = "value1"
        expected_msg = "Invalid value for input {} : {}".format(name, value)
        expected_code = 400
        error = InputValueError(name, value)
        self.assertEqual(error.msg, expected_msg)
        self.assertEqual(error.code, expected_code)

    def test_init_EntityNotFoundError(self):
        """test the init method."""
        id = "id1"
        expected_msg = "Entity not found for {}".format(id)
        expected_code = 404
        error = EntityNotFoundError(id)
        self.assertEqual(error.msg, expected_msg)
        self.assertEqual(error.code, expected_code)
