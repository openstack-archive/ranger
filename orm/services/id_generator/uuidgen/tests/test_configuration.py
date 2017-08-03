"""Get configuration module unittests."""
from mock import patch
from uuidgen.controllers.v1 import configuration as root
from uuidgen.tests import FunctionalTest


class TestGetConfiguration(FunctionalTest):
    """Main get configuration test case."""

    @patch.object(root.utils, 'report_config', return_value='12345')
    def test_get_configuration_success(self, input):
        """Test get_configuration returns the expected value on success."""
        response = self.app.get('/v1/configuration')
        self.assertEqual(response.json, '12345')
