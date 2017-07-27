"""Logs module unittests."""
from fms_rest.tests import FunctionalTest


class TestLogs(FunctionalTest):
    """logs tests."""

    def test_change_log_level_fail(self):
        response = self.app.put('/v1/orm/logs/1')
        expected_result = {
            "result": "Fail to change log_level. Reason: "
            "The given log level [1] doesn't exist."}
        self.assertEqual(expected_result, response.json)

    def test_change_log_level_none(self):
        response = self.app.put('/v1/orm/logs', expect_errors=True)
        expected_result = 'Missing argument: "level"'
        self.assertEqual(response.json["faultstring"], expected_result)
        self.assertEqual(response.status_code, 400)

    def test_change_log_level_success(self):
        response = self.app.put('/v1/orm/logs/debug')
        expected_result = {'result': 'Log level changed to debug.'}
        self.assertEqual(response.json, expected_result)
        self.assertEqual(response.status_code, 201)
