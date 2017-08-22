from orm.services.flavor_manager.fms_rest.utils import authentication
from orm.tests.unit.fms import FunctionalTest

import mock
from pecan import conf


class TestUtil(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        self.mock_response = mock.Mock()

    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.TokenConf')
    def test_get_token_conf(self, mock_TokenConf):
        mock_TokenConf.return_value = 123
        token_conf = authentication.get_token_conf(conf)
        self.assertEqual(token_conf, 123)

    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.is_token_valid')
    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.TokenConf')
    def test_check_permissions_token_valid(self, mock_get_token_conf, mock_is_token_valid):
        setattr(conf.authentication, 'enabled', True)
        mock_get_token_conf.return_value = 123
        mock_is_token_valid.return_value = True
        is_permitted = authentication.check_permissions(conf, 'asher', 0)
        self.assertEqual(is_permitted, True)

    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.is_token_valid')
    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.TokenConf')
    def test_check_permissions_token_invalid(self, mock_get_token_conf, mock_is_token_valid):
        setattr(conf.authentication, 'enabled', True)
        mock_get_token_conf.return_value = 123
        mock_is_token_valid.return_value = False
        is_permitted = authentication.check_permissions(conf, 'asher', 0)
        self.assertEqual(is_permitted, False)

    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.is_token_valid')
    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.TokenConf')
    def test_check_permissions_disabled(self, mock_get_token_conf, mock_is_token_valid):
        setattr(conf.authentication, 'enabled', False)
        mock_get_token_conf.return_value = 123
        mock_is_token_valid.return_value = False
        is_permitted = authentication.check_permissions(conf, 'asher', 0)
        self.assertEqual(is_permitted, True)

    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.is_token_valid')
    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.TokenConf')
    def test_check_permissions_is_token_valid_breaks(self, mock_get_token_conf, mock_is_token_valid):
        setattr(conf.authentication, 'enabled', True)
        mock_is_token_valid.side_effect = Exception('boom')
        is_permitted = authentication.check_permissions(conf, 'asher', 0)
        self.assertEqual(is_permitted, False)
