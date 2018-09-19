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

