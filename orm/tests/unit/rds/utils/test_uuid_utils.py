"""UUID utils test module."""


class MyResponse(object):
    """A test response class."""

    def json(self):
        """Return the test dict."""
        return {'uuid': 3}


# class UuidUtilsTest(unittest.TestCase):
#     """The main UUID utils test case."""
#
#     @mock.patch.object(uuid_utils, 'config')
#     @mock.patch.object(uuid_utils.requests, 'post', return_value=MyResponse())
#     def test_get_random_uuid_sanity(self, mock_post, mock_config):
#         """Test that the function returns the expected value."""
#         self.assertEqual(uuid_utils.get_random_uuid(), 3)
#
#     @mock.patch.object(uuid_utils, 'config')
#     @mock.patch.object(uuid_utils.requests, 'post', side_effect=ValueError(
#         'test'))
#     def test_get_random_uuid_exception(self, mock_post, mock_config):
#         """Test that the function lets exceptions propagate."""
#         self.assertRaises(ValueError, uuid_utils.get_random_uuid)
