import mock
import unittest

from orm_common.policy import policy
from orm_common.utils import api_error_utils as err_utils


class TestException(Exception):
    pass


class TestPolicy(unittest.TestCase):
    def setUp(self):
        policy._ENFORCER = None
        policy._POLICY_FILE = None
        policy._TOKEN_CONF = None

    def test_reset(self):
        policy._ENFORCER = mock.MagicMock()
        policy._POLICY_FILE = mock.MagicMock()
        policy.reset()
        self.assertIsNone(policy._ENFORCER)
        self.assertIsNone(policy._POLICY_FILE)
        # Call it a second time when they are both None and see
        # that no exception is raised
        policy.reset()
        self.assertIsNone(policy._ENFORCER)
        self.assertIsNone(policy._POLICY_FILE)

    @mock.patch.object(policy, 'open')
    @mock.patch.object(policy.qolicy, 'Enforcer')
    @mock.patch.object(policy.qolicy, 'Rules')
    def test_init_success(self, mock_rules, mock_enforcer, mock_open):
        policy_file = 'a'
        token_conf = 'b'
        mock_rules.load_json.return_value = 'c'
        policy.init(policy_file, token_conf)
        self.assertEqual(policy._POLICY_FILE, 'a')
        self.assertEqual(policy._TOKEN_CONF, 'b')

    def test_init_enforcer_already_exists(self):
        policy._ENFORCER = mock.MagicMock()

        # Nothing should happen when the enforcer already exists, so make sure
        # that no exception is raised
        policy.init('a', 'b')

    @mock.patch.object(policy, 'open')
    @mock.patch.object(policy.qolicy, 'Rules')
    @mock.patch.object(policy, '_ENFORCER')
    def test_reset_rules_no_policy_file(self, mock_enforcer,
                                        mock_rules, mock_open):
        self.assertRaises(ValueError, policy.reset_rules)

    @mock.patch.object(policy, 'open')
    @mock.patch.object(policy.qolicy, 'Rules')
    @mock.patch.object(policy, '_ENFORCER')
    def test_reset_rules_success(self, mock_enforcer,
                                 mock_rules, mock_open):
        policy._POLICY_FILE = mock.MagicMock()
        policy.reset_rules()
        self.assertTrue(mock_enforcer.set_rules.called)

    @mock.patch.object(policy, 'reset_rules')
    @mock.patch.object(policy.tokens, 'get_token_user',
                       side_effect=ValueError('test'))
    @mock.patch.object(policy, '_ENFORCER')
    def test_enforce_enforcer_error(self, mock_enforcer,
                                    mock_get_token_user,
                                    mock_reset_rules):
        mock_enforcer.enforce.side_effect = policy.EnforcerError()
        self.assertRaises(policy.EnforcerError, policy.enforce, 'action',
                          'token', mock.MagicMock())

    @mock.patch.object(policy, 'reset_rules')
    @mock.patch.object(policy.tokens, 'get_token_user')
    @mock.patch.object(policy, '_ENFORCER')
    def test_enforce_success(self, mock_enforcer,
                             mock_get_token_user,
                             mock_reset_rules):
        mock_enforcer.enforce.return_value = True
        self.assertTrue(policy.enforce('action', 'token', mock.MagicMock()))

    def test_authorize_authorization_disabled(self):
        request = mock.MagicMock()
        app_conf = mock.MagicMock()
        app_conf.authentication.enabled = False
        # No exception should be raised
        policy.authorize('a', request, app_conf)

    @mock.patch.object(policy, 'enforce')
    def test_authorize_no_token(self, mock_enforce):
        request = mock.MagicMock()
        request.headers.get.return_value = None
        app_conf = mock.MagicMock()
        app_conf.authentication.enabled = True
        # No exception should be raised
        policy.authorize('a', request, app_conf)

    @mock.patch.object(policy, 'enforce', side_effect=policy.EnforcerError())
    @mock.patch.object(policy.err_utils, 'get_error', return_value=TestException)
    def test_authorize_enforce_failed(self, mock_enforce, mock_get_error):
        request = mock.MagicMock()
        request.headers.get.return_value = None
        app_conf = mock.MagicMock()
        app_conf.authentication.enabled = True

        self.assertRaises(TestException, policy.authorize, 'a', request,
                          app_conf)

    @mock.patch.object(policy, 'enforce', side_effect=ValueError())
    @mock.patch.object(policy.err_utils, 'get_error', return_value=TestException)
    def test_authorize_other_error(self, mock_enforce, mock_get_error):
        request = mock.MagicMock()
        request.headers.get.return_value = None
        app_conf = mock.MagicMock()
        app_conf.authentication.enabled = True

        self.assertRaises(TestException, policy.authorize, 'a', request,
                          app_conf)

    @mock.patch.object(policy, 'enforce')
    def test_authorize_success(self, mock_enforce):
        request = mock.MagicMock()
        request.headers.get.return_value = 'test'
        app_conf = mock.MagicMock()
        app_conf.authentication.enabled = True

        # No exception should be raised
        policy.authorize('a', request, app_conf)
