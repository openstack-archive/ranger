from ormcli import cli_common
import mock
from unittest import TestCase


class CmsTests(TestCase):
    @mock.patch.object(cli_common.requests, 'get')
    def test_get_keystone_ep_sanity(self, mock_get):
        my_response = mock.MagicMock()
        my_response.status_code = cli_common.OK_CODE
        my_response.json.return_value = {
            'regions': [{'endpoints': [{
                'type': 'identity', 'publicURL': 'test'}]}]}
        mock_get.return_value = my_response

        self.assertEqual(cli_common.get_keystone_ep('a', 'b'), 'test')

    @mock.patch.object(cli_common.requests, 'get',
                       side_effect=cli_common.requests.exceptions
                       .ConnectionError())
    def test_get_keystone_ep_connection_failed(self, mock_get):
        self.assertIsNone(cli_common.get_keystone_ep('a', 'b'))


@mock.patch.object(cli_common.requests, 'get')
def test_get_keystone_ep_bad_status_code(self, mock_get):
    my_response = mock.MagicMock()
    my_response.status_code = cli_common.OK_CODE + 1
    my_response.json.return_value = {
        'regions': [{'endpoints': [{
            'type': 'identity', 'publicURL': 'test'}]}]}
    mock_get.return_value = my_response

    self.assertIsNone(cli_common.get_keystone_ep('a', 'b'))


@mock.patch.object(cli_common.requests, 'get')
def test_get_keystone_ep_bad_response(self, mock_get):
    my_response = mock.MagicMock()
    my_response.status_code = cli_common.OK_CODE
    my_response.json.return_value = {
        'regions': [{'endpoinqs': [{
            'type': 'identity', 'publicURL': 'test'}]}]}
    mock_get.return_value = my_response

    self.assertIsNone(cli_common.get_keystone_ep('a', 'b'))

    my_response.json.return_value = {
        'regions': [{'endpoints': [{
            'type': 'identiqy', 'publicURL': 'test'}]}]}
    mock_get.return_value = my_response

    self.assertIsNone(cli_common.get_keystone_ep('a', 'b'))
