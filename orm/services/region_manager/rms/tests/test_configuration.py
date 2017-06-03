"""Get configuration module unittests."""
from mock import patch
from rms.controllers import configuration as root
from rms.tests import FunctionalTest


class TestGetConfiguration(FunctionalTest):
    """Main get configuration test case."""

    @patch.object(root.utils, 'report_config', return_value='12345')
    @patch.object(root, 'authentication')
    def test_get_configuration_success(self, mock_authentication, input):
        """Test get_configuration returns the expected value on success."""
        response = self.app.get('/configuration')
        self.assertEqual(response.json, '12345')
