import json

from mock import patch
from rms.controllers.v2.orm.resources import status
from rms.tests import FunctionalTest
from wsme.exc import ClientSideError


def get_region_status_data(status):
    return {
        "status": status,
        "links": {
            "self": "https://0.0.0.0:8080/v2/orm/regions/my_region/status",
        }
    }


class TestRegionStatus(FunctionalTest):
    @patch.object(status, 'request')
    @patch.object(status.utils, 'audit_trail')
    @patch.object(status.RegionService, 'update_region_status')
    @patch.object(status.authentication, 'authorize', return_value=True)
    def test_update_region_status_success(self,
                                          auth,
                                          mock_update_status_logic,
                                          mock_audit_trail,
                                          mock_request):
        self.maxDiff = None
        mock_update_status_logic.return_value = "functional"
        response = self.app.put_json('/v2/orm/regions/my_region/status',
                                     get_region_status_data("functional"))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, get_region_status_data("functional"))

    @patch.object(status, 'request')
    @patch.object(status, 'err_utils')
    @patch.object(status.RegionService, 'update_region_status')
    @patch.object(status.authentication, 'authorize', return_value=True)
    def test_update_region_status_invalid_status(self, auth,
                                                 update_region_status,
                                                 mock_err_util,
                                                 request_mock):
        mock_err_util.get_error = get_error
        request_mock.transaction_id = "555"
        response = self.app.put_json('/v2/orm/regions/my_region/status',
                                     get_region_status_data("invalid_status"),
                                     expect_errors=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         "Invalid status. Region status must be one "
                         "of ['functional', 'maintenance', 'down']")

    @patch.object(status, 'request')
    @patch.object(status, 'err_utils')
    @patch.object(status.RegionService, 'update_region_status')
    @patch.object(status.authentication, 'authorize', return_value=True)
    def test_update_region_status_unknown_error(self, auth,
                                                update_region_status,
                                                mock_err_util,
                                                request_mock):
        mock_err_util.get_error = get_error
        request_mock.transaction_id = "555"
        update_region_status.side_effect = Exception("unknown error")
        response = self.app.put_json('/v2/orm/regions/my_region/status',
                                     get_region_status_data("functional"),
                                     expect_errors=True)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         "unknown error")


def get_error(transaction_id, status_code, error_details=None, message=None):
    return ClientSideError(json.dumps({
        'code': status_code,
        'type': 'test',
        'created': '0.0',
        'transaction_id': transaction_id,
        'message': message if message else error_details,
        'details': 'test'
    }), status_code=status_code)
