import json
from unittest import TestCase

import mock
from orm_common.utils import api_error_utils


class TestCrossApiUtil(TestCase):
    @mock.patch.object(api_error_utils.utils, 'get_time_human', return_value=1.337)
    def test_get_error_default_message(self, mock_time):
        self.assertEqual(
            json.loads(api_error_utils.get_error('test', 'a').message),
            {"details": "a", "message": "Incompatible JSON body",
             "created": "1.337", "code": 400, "type": "Bad Request",
             "transaction_id": "test"})
