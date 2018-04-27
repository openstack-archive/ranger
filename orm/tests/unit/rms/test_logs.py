import json
import logging

from mock import patch, MagicMock
from wsme.exc import ClientSideError

import orm.services.region_manager.rms.controllers.logs as logs
from orm.services.region_manager.rms.controllers.logs import LogsController as logs_controller
from orm.tests.unit.rms import FunctionalTest


class TestGetConfiguration(FunctionalTest):

    @patch.object(logging, 'getLogger')
    def test_change_log_level_success(self, input):
        logs_controller._change_log_level(50)

    @patch.object(logs_controller, '_change_log_level')
    @patch.object(logs, 'authentication')
    def test_put_success(self, mock_authentication, err):
        response = self.app.put('/logs/info', expect_errors=True)
        self.assertEqual(response.status_int, 201)

    @patch.object(logs_controller, '_change_log_level')
    @patch.object(logs.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '333',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    @patch.object(logs, 'authentication')
    def test_put_failed_wrong_log_level(self, mock_auth, err, err2):
        temp_request = logs.request
        logs.request = MagicMock()

        response = self.app.put('/logs/info000', expect_errors=True)

        logs.request = temp_request

        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual("333", result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])
