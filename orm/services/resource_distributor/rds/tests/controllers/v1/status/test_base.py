import unittest

from rds.controllers.v1.base import ClientSideError


class Test(unittest.TestCase):

    # Test the creation of ClientSideError
    def test_ClientSideError(self):
        error_str = "This is an error message"
        clientSideError = ClientSideError(error=error_str)
        self.assertEqual(clientSideError.msg, error_str)
        self.assertEqual(clientSideError.code, 400)
