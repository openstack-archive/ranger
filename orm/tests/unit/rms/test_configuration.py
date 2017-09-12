"""Get configuration module unittests."""
from orm.services.region_manager.rms.controllers import configuration as root
from orm.tests.unit.rms import FunctionalTest

from mock import patch


class TestGetConfiguration(FunctionalTest):
    """Main get configuration test case."""

    @patch.object(root.utils, 'report_config', return_value='12345')
    @patch.object(root, 'authentication')
    def test_get_configuration_success(self, mock_authentication, input):
        """Test get_configuration returns the expected value on success."""
        response = self.app.get('/configuration')
        self.assertEqual(response.json, '12345')
