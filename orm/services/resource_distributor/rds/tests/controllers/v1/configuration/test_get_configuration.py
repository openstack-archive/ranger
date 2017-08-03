"""Get configuration module unittests."""
from mock import patch
from rds.controllers.v1.configuration import root
from rds.tests.controllers.v1.functional_test import FunctionalTest


class TestGetConfiguration(FunctionalTest):
    """Main get configuration test case."""
    @patch.object(root, 'utils')
    def test_get_configuration_success(self, mock_utils):
        """test get config success."""
        mock_utils.set_utils_conf.return_value = True
        mock_utils.report_config.return_value = "1234"
        response = self.app.get('/v1/rds/configuration')
        self.assertEqual(response.json, '1234')

    # @patch.object(root.utils, 'report_config', return_value='12345')
    # def test_get_configuration_success(self, input):
    #     """Test get_configuration returns the expected value on success."""
    #     response = self.app.get('/v1/rds/configuration')
    #     self.assertEqual(response.json, '12345')
