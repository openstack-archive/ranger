import json
import logging
from unittest import TestCase

import mock
from orm.common.orm_common.hooks import api_error_hook

logger = logging.getLogger(__name__)


class TestAPIErrorHook(TestCase):
    @mock.patch.object(api_error_hook, 'err_utils')
    @mock.patch.object(api_error_hook, 'json')
    def test_after_401(self, mock_json, mock_err_utils):
        a = api_error_hook.APIErrorHook()
        state = mock.MagicMock()

        mock_err_utils.get_error_dict.return_value = 'B'
        mock_json.loads = json.loads
        mock_json.dumps = json.dumps
        state.response.status_code = 401
        a.after(state)
        self.assertEqual(state.response.body,
                         json.dumps(mock_err_utils.get_error_dict.return_value))

    @mock.patch.object(api_error_hook, 'err_utils')
    def test_after_not_an_error(self, mock_err_utils):
        a = api_error_hook.APIErrorHook()
        state = mock.MagicMock()

        mock_err_utils.get_error_dict.return_value = 'B'
        state.response.body = 'AAAA'
        temp = state.response.body
        # A successful status code
        state.response.status_code = 201
        a.after(state)
        # Assert that the response body hasn't changed
        self.assertEqual(state.response.body, temp)

    @mock.patch.object(api_error_hook, 'err_utils')
    @mock.patch.object(api_error_hook.json, 'loads',
                       side_effect=ValueError('test'))
    def test_after_error(self, mock_json, mock_err_utils):
        a = api_error_hook.APIErrorHook()
        state = mock.MagicMock()

        mock_err_utils.get_error_dict.return_value = 'B'
        state.response.body = 'AAAA'

        mock_json.loads = mock.MagicMock(side_effect=ValueError('sd'))
        state.response.status_code = 402
        a.after(state)
        self.assertEqual(state.response.body,
                         json.dumps(mock_err_utils.get_error_dict.return_value))

    @mock.patch.object(api_error_hook, 'err_utils')
    @mock.patch.object(api_error_hook, 'json')
    def test_after_success(self, mock_json, mock_err_utils):
        a = api_error_hook.APIErrorHook()
        state = mock.MagicMock()

        mock_err_utils.get_error_dict.return_value = 'B'
        mock_json.loads = json.loads
        mock_json.dumps = json.dumps
        mock_json.loads = json.loads
        state.response.body = '{"debuginfo": null, "faultcode": "Client", "faultstring": "{\\"code\\": 404, \\"created\\": \\"1475768730.95\\", \\"details\\": \\"\\", \\"message\\": \\"customer: q not found\\", \\"type\\": \\"Not Found\\", \\"transaction_id\\": \\"mock_json5efa7416fb4d408cc0e30e4373cf00\\"}"}'
        state.response.status_code = 400
        a.after(state)
        self.assertEqual(json.loads(state.response.body), json.loads('{"message": "customer: q not found", "created": "1475768730.95", "type": "Not Found", "details": "", "code": 404, "transaction_id": "mock_json5efa7416fb4d408cc0e30e4373cf00"}'))
