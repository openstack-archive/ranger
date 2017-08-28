"""Get configuration module unittests."""
from orm.tests.unit.fms import FunctionalTest

from mock import patch


class TestGetConfiguration(FunctionalTest):
    """Main get configuration test case."""

    @patch('orm.common.orm_common.utils.utils.report_config')
    def test_get_configuration_success(self, mock_report):
        """Test get_configuration returns the expected value on success."""
        mock_report.return_value = '12345'
        response = self.app.get('/v1/orm/configuration')
        self.assertEqual(response.json, '12345')
