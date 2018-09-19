import mock
from pecan import conf

from orm.services.customer_manager.cms_rest.utils import authentication
from orm.tests.unit.cms import FunctionalTest


class TestUtil(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        self.mock_response = mock.Mock()

    @mock.patch('orm.common.client.keystone.keystone_utils.tokens.TokenConf')
    def test_get_token_conf(self, mock_TokenConf):
        mock_TokenConf.return_value = 123
        token_conf = authentication._get_token_conf(conf)
        self.assertEqual(token_conf, 123)
