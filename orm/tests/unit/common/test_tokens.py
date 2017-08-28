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

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    @mock.patch.object(tokens.v3_client, 'Client')
    def test_is_token_valid_sanity(self, mock_get, mock_client):
        self.assertTrue(tokens.is_token_valid('a', 'b', tokens.TokenConf(
            'a', 'b', 'c', 'd', '3')))

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    @mock.patch.object(tokens.v3_client, 'Client')
    def test_is_token_valid_sanity_role_required(self, mock_get, mock_client):
        user = {'user': {'id': 'test_id', 'domain': {'id': 'test'}}}
        mock_client.tokens.validate = mock.MagicMock(return_value=user)
        self.assertTrue(tokens.is_token_valid('a', 'b', tokens.TokenConf(
            'a', 'b', 'c', 'd', '3'), 'test', {'domain': 'test'}))

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    def test_is_token_valid_token_not_found(self, mock_get):
        client_backup = tokens.v3_client.Client
        tokens.v3_client.Client = mock.MagicMock(return_value=MyClient())
        self.assertFalse(tokens.is_token_valid('a', 'b', tokens.TokenConf(
            'a', 'b', 'c', 'd', '3')))
        tokens.v3_client.Client = client_backup

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    def test_is_token_valid_invalid_version(self, mock_get):
        client_backup = tokens.v3_client.Client
        tokens.v3_client.Client = mock.MagicMock(return_value=MyClient())
        self.assertRaises(ValueError, tokens.is_token_valid, 'a', 'b',
                          tokens.TokenConf('a', 'b', 'c', 'd', '4'))
        tokens.v3_client.Client = client_backup

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    def test_is_token_valid_keystone_v2(self, mock_get):
        client_backup = tokens.v2_client.Client
        tokens.v2_client.Client = mock.MagicMock()
        self.assertFalse(tokens.is_token_valid('a', 'b',
                                               tokens.TokenConf('a', 'b', 'c',
                                                                'd', '2.0'),
                                               'test',
                                               {'tenant': 'test'}))
        tokens.v2_client.Client = client_backup

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    def test_is_token_valid_keystone_v2_invalid_location(self, mock_get):
        client_backup = tokens.v2_client.Client
        tokens.v2_client.Client = mock.MagicMock()
        self.assertRaises(ValueError, tokens.is_token_valid, 'a', 'b',
                          tokens.TokenConf('a', 'b', 'c', 'd', '2.0'), 'test',
                          {'domain': 'test'})
        tokens.v2_client.Client = client_backup

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE + 1, {'regions': [{'endpoints': [
            {'publicURL': 'test', 'type': 'identity'}]}]}))
    def test_is_token_valid_keystone_ep_not_found(self, mock_get):
        self.assertRaises(tokens.KeystoneNotFoundError, tokens.is_token_valid,
                          'a', 'b', tokens.TokenConf('a', 'b', 'c', 'd', '3'))

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    def test_is_token_valid_no_role_location(self, mock_get):
        tokens.v3_client.Client = mock.MagicMock()
        self.assertRaises(ValueError, tokens.is_token_valid, 'a', 'b',
                          tokens.TokenConf('a', 'b', 'c', 'd', '3'), 'test')

    @mock.patch.object(tokens.v3_client, 'Client')
    def test_does_user_have_role_sanity_true(self, mock_client):
        user = {'user': {'id': 'test_id', 'domain': {'id': 'test'}}}
        self.assertTrue(tokens._does_user_have_role(mock_client, '3', user,
                                                    'admin',
                                                    {'domain': 'test'}))

    @mock.patch.object(tokens.v3_client, 'Client')
    def test_does_user_have_role_sanity_false(self, mock_client):
        user = {'user': {'id': 'test_id', 'domain': {'id': 'test'}}}
        mock_client.roles.check = mock.MagicMock(
            side_effect=exceptions.NotFound('test'))
        self.assertFalse(tokens._does_user_have_role(mock_client, '3', user,
                                                     'admin',
                                                     {'domain': 'test'}))

    @mock.patch.object(tokens.v3_client, 'Client')
    def test_does_user_have_role_invalid_user(self, mock_client):
        user = {}
        self.assertFalse(tokens._does_user_have_role(mock_client, '3', user,
                                                     'admin',
                                                     {'domain': 'test'}))

    @mock.patch.object(tokens.v3_client, 'Client')
    def test_does_user_have_role_role_does_not_exist(self, mock_client):
        user = {'user': {'id': 'test_id', 'domain': {'id': 'test'}}}
        mock_client.roles.find = mock.MagicMock(
            side_effect=exceptions.NotFound('test'))
        self.assertRaises(exceptions.NotFound,
                          tokens._does_user_have_role, mock_client, '3',
                          user, 'test', {'domain': 'default'})

    @mock.patch.object(tokens.requests, 'get', return_value=MyResponse(
        tokens.OK_CODE, {'regions': [{'endpoints': [{'publicURL': 'test',
                                                     'type': 'identity'}]}]}))
    def test_is_token_valid_role_does_not_exist(self, mock_get):
        tokens.v3_client.Client = mock.MagicMock(return_value=MyClient(False))
        self.assertRaises(ValueError, tokens.is_token_valid, 'a', 'b',
                          tokens.TokenConf('a', 'b', 'c', 'd', '3'), 'test',
                          {'domain': 'test'})

    def test_get_token_user_invalid_arguments(self):
        self.assertRaises(ValueError, tokens.get_token_user, 'a', 'b')

    @mock.patch.object(tokens, '_find_keystone_ep', return_value=None)
    def test_get_token_user_keystone_ep_not_found(self,
                                                  mock_find_keystone_ep):
        self.assertRaises(tokens.KeystoneNotFoundError,
                          tokens.get_token_user, 'a', mock.MagicMock(), 'c')

    def test_get_token_user_invalid_keystone_version(self):
        conf = tokens.TokenConf(*(None,) * 5)
        self.assertRaises(ValueError, tokens.get_token_user, 'a', conf, 'c',
                          'd')

    @mock.patch.object(tokens, '_get_keystone_client')
    def test_get_token_user_token_not_found(self, mock_get_keystone_client):
        ks = mock.MagicMock()
        ks.tokens.validate.side_effect = exceptions.NotFound()
        mock_get_keystone_client.return_value = ks
        conf = tokens.TokenConf(*('3',) * 5)
        self.assertIsNone(tokens.get_token_user('a', conf, 'c', 'd'))

    @mock.patch.object(tokens, '_get_keystone_client')
    def test_get_token_user_success(self, mock_get_keystone_client):
        token_info = mock.MagicMock()
        token_info.token = 'a'
        token_info.user = 'test_user'
        ks = mock.MagicMock()
        ks.tokens.validate.return_value = token_info
        mock_get_keystone_client.return_value = ks

        conf = tokens.TokenConf(*('2.0',) * 5)
        result = tokens.get_token_user('a', conf, 'c', 'd')

        self.assertEqual(result.token, 'a')
        self.assertEqual(result.user, 'test_user')
