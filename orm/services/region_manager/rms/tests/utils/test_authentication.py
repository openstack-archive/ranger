"""Authentication utilities module unittests."""
import mock
from rms.tests import FunctionalTest
from rms.utils import authentication


class TestGetConfiguration(FunctionalTest):
    """Main authentication test case."""

    @mock.patch.object(authentication.policy, 'authorize')
    @mock.patch.object(authentication, '_get_keystone_ep')
    @mock.patch.object(authentication, '_is_authorization_enabled')
    def test_authorize_success(self, mock_iae, mock_gke, mock_authorize):
        request = mock.MagicMock()
        action = 'test:test'

        # Success when authentication is disabled
        mock_iae.return_value = False
        authentication.authorize(request, action)

        # Success when authentication is enabled
        mock_iae.return_value = True
        authentication.authorize(request, action)

    def mock_authorize_no_keystone(self, *args, **kwargs):
        self.assertIsNone(kwargs['keystone_ep'])

    @mock.patch.object(authentication, 'policy')
    @mock.patch.object(authentication, '_get_keystone_ep')
    @mock.patch.object(authentication, '_is_authorization_enabled')
    def test_authorize_gke_failed(self, mock_iae, mock_gke, mock_policy):
        request = mock.MagicMock()
        action = 'test:test'

        # Success when authentication is disabled
        mock_iae.return_value = False
        authentication.authorize(request, action)

        # Success when authentication is enabled
        mock_iae.return_value = True
        authentication.authorize(request, action)

    @mock.patch.object(authentication, 'policy')
    @mock.patch.object(authentication, '_get_keystone_ep',
                       side_effect=ValueError('test'))
    @mock.patch.object(authentication, '_is_authorization_enabled',
                       return_value=True)
    def test_authorize_gke_failed(self, mock_iae, mock_gke, mock_policy):
        request = mock.MagicMock()
        action = 'test:test'

        mock_policy.authorize = self.mock_authorize_no_keystone
        authentication.authorize(request, action)

    def test_is_authorization_enabled(self):
        app_conf = mock.MagicMock()

        app_conf.authentication.enabled = True
        self.assertTrue(authentication._is_authorization_enabled(app_conf))

        app_conf.authentication.enabled = False
        self.assertFalse(authentication._is_authorization_enabled(app_conf))

    @mock.patch.object(authentication.RegionService,
                       'get_region_by_id_or_name')
    def test_get_keystone_ep_success(self, mock_grbion):
        region = mock.MagicMock()
        keystone_ep = mock.MagicMock()
        keystone_ep.type = 'identity'
        keystone_ep.publicurl = 'test'
        region.endpoints = [keystone_ep]
        mock_grbion.return_value = region

        self.assertEqual(authentication._get_keystone_ep('region'),
                         keystone_ep.publicurl)

    @mock.patch.object(authentication.RegionService,
                       'get_region_by_id_or_name')
    def test_get_keystone_ep_no_keystone_ep(self, mock_grbion):
        self.assertIsNone(authentication._get_keystone_ep('region'))
