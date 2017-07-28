"""Get configuration module unittests."""
from audit_server.controllers.v1 import configuration as root
from audit_server.tests.controllers.v1.functional_test import FunctionalTest
from mock import patch


class TestGetConfiguration(FunctionalTest):
    """Main get configuration test case."""

    @patch.object(root.utils, 'report_config', return_value='12345')
    def test_get_configuration_success(self, input):
        """Test get_configuration returns the expected value on success."""
        response = self.app.get('/v1/audit/configuration')
        self.assertEqual(response.json, '12345')
