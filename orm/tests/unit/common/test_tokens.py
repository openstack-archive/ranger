"""keystone_utils token validator unittests."""
import unittest

from orm.common.client.keystone.keystone_utils import tokens
from orm.common.client.keystone.mock_keystone.keystoneclient import exceptions

import mock


class MyResponse(object):
    def __init__(self, status, json_result):
        self.status_code = status
        self._json_result = json_result

    def json(self):
        return self._json_result


class MyKeystone(object):
    def validate(self, a):
        raise exceptions.NotFound('test')

    def find(self, **kwargs):
        raise exceptions.NotFound('test')


class MyClient(object):
    def __init__(self, set_tokens=True):
        if set_tokens:
            self.tokens = MyKeystone()
        else:
            self.tokens = mock.MagicMock()

        self.roles = MyKeystone()


class TokensTest(unittest.TestCase):
    def setUp(self):
        tokens._KEYSTONES = {}

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    def test_find_keystone_ep_sanity(self, mock_get):
        result = tokens._find_keystone_ep('a', 'b')
        self.assertEqual(result, 'test')

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE + 1, {'regions': [{'endpoints': [
            {'publicURL': 'test', 'type': 'identity'}]}]}))
    def test_find_keystone_ep_bad_return_code(self, mock_get):
        result = tokens._find_keystone_ep('a', 'b')
        self.assertIsNone(result)

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {}))
    def test_find_keystone_ep_no_keystone_ep_in_response(self, mock_get):
        result = tokens._find_keystone_ep('a', 'b')
        self.assertIsNone(result)

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'test'}]}]}))
    def test_find_keystone_ep_no_identity_in_response(self, mock_get):
        result = tokens._find_keystone_ep('a', 'b')
        self.assertIsNone(result)

    # @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
    #    tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
    #                                                 'type': 'identity'}]}]}))
    # @mock.patch.object(tokens, '_get_keystone_client')
    # def test_get_token_user_token_not_found(self, mock_get_keystone_client):
    #    import pdb
    #    pdb.set_trace()
    #    ks = mock.MagicMock()
    #    ks.tokens.validate.side_effect = exceptions.NotFound()
    #    mock_get_keystone_client.return_value = ks
    #    conf = tokens.TokenConf(*('3',) * 7)
    #    self.assertIsNone(tokens.get_token_user('a', conf, 'c', 'd'))

    # @mock.patch.object(tokens, 'request')
    # @mock.patch.object(tokens, '_get_keystone_client')
    # def test_get_token_user_success(self, mock_get_keystone_client,
    #                                mock_request):
    #    token_info = mock.MagicMock()
    #    token_info.token = 'a'
    #    token_info.user = 'test_user'
    #    ks = mock.MagicMock()
    #    ks.tokens.validate.return_value = token_info
    #    mock_get_keystone_client.return_value = ks

    #    conf = tokens.TokenConf(*('3',) * 7)
    #    result = tokens.get_token_user('a', conf, 'c', 'd')

    #    self.assertEqual(result.token, 'a')
    #    self.assertEqual(result.user, 'test_user')
