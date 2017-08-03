import logging
import pprint
from unittest import TestCase

import mock
from orm_common.utils import utils
from testfixtures import log_capture


class TestUtil(TestCase):
    @mock.patch('pecan.conf')
    def setUp(self, mock_conf):
        self.mock_response = mock.Mock()
        utils.conf = mock_conf

    def respond(self, value, code):
        self.mock_response.json.return_value = value
        self.mock_response.status_code = code
        return self.mock_response

    @mock.patch('requests.post')
    def test_make_uuid(self, mock_post):
        mock_post.return_value = self.respond({'uuid': '987654321'}, 200)
        uuid = utils.make_uuid()
        self.assertEqual(uuid, '987654321')

    @mock.patch('requests.post')
    @log_capture('orm_common.utils.utils', level=logging.INFO)
    def test_make_uuid_offline(self, mock_post, l):
        mock_post.side_effect = Exception('boom')
        uuid = utils.make_uuid()
        self.assertEqual(uuid, None)
        l.check(('orm_common.utils.utils', 'INFO', 'Failed in make_uuid:boom'))

    @mock.patch('requests.post')
    def test_make_transid(self, mock_post):
        mock_post.return_value = self.respond({'uuid': '987654321'}, 200)
        uuid = utils.make_transid()
        self.assertEqual(uuid, '987654321')

    @mock.patch('requests.post')
    @log_capture('orm_common.utils.utils', level=logging.INFO)
    def test_make_transid_offline(self, mock_post, l):
        mock_post.side_effect = Exception('boom')
        uuid = utils.make_transid()
        self.assertEqual(uuid, None)
        l.check(
            ('orm_common.utils.utils', 'INFO', 'Failed in make_transid:boom'))

    @mock.patch('audit_client.api.audit.init')
    @mock.patch('audit_client.api.audit.audit')
    def test_audit_trail(self, mock_init, mock_audit):
        resp = utils.audit_trail('create customer', '1234',
                                 {'X-RANGER-Client': 'Fred'}, '5678')
        self.assertEqual(resp, 200)

    @mock.patch('audit_client.api.audit.audit')
    def test_audit_trail_offline(self, mock_audit):
        mock_audit.side_effect = Exception('boom')
        resp = utils.audit_trail('create customer', '1234',
                                 {'X-RANGER-Client': 'Fred'}, '5678')
        self.assertEqual(resp, None)

    @mock.patch('audit_client.api.audit.init')
    @mock.patch('audit_client.api.audit.audit')
    def test_audit_service_args_least(self, mock_audit, mock_init):
        resp = utils.audit_trail('create customer', '1234',
                                 {'X-RANGER-Client': 'Fred'}, '5678')
        self.assertEqual(mock_audit.call_args[0][1], 'Fred')  # application_id
        self.assertEqual(mock_audit.call_args[0][2], '1234')  # tracking_id
        self.assertEqual(mock_audit.call_args[0][3], '1234')  # transaction_id
        self.assertEqual(mock_audit.call_args[0][4],
                         'create customer')  # transaction_type
        self.assertEqual(mock_audit.call_args[0][5], '5678')  # resource_id
        # self.assertEqual(mock_audit.call_args[0][6], 'cms')  # service
        self.assertEqual(mock_audit.call_args[0][7], '')  # user_id
        self.assertEqual(mock_audit.call_args[0][8], 'NA')  # external_id
        self.assertEqual(mock_audit.call_args[0][9], 'CMS')  # event_details
        # self.assertEqual(mock_audit.call_args[0][10], 'Saved to DB')  # status

    @mock.patch('audit_client.api.audit.init')
    @mock.patch('audit_client.api.audit.audit')
    def test_audit_service_with_tracking(self, mock_audit, mock_init):
        utils.audit_trail('create customer', '1234',
                          {'X-RANGER-Client': 'Fred',
                           'X-RANGER-Tracking-Id': 'Track12'}, '5678')
        self.assertEqual(mock_audit.call_args[0][1], 'Fred')  # application_id
        self.assertEqual(mock_audit.call_args[0][2], 'Track12')  # tracking_id
        self.assertEqual(mock_audit.call_args[0][3], '1234')  # transaction_id
        self.assertEqual(mock_audit.call_args[0][4],
                         'create customer')  # transaction_type
        self.assertEqual(mock_audit.call_args[0][5], '5678')  # resource_id
        # self.assertEqual(mock_audit.call_args[0][6], 'cms')  # service
        self.assertEqual(mock_audit.call_args[0][7], '')  # user_id
        self.assertEqual(mock_audit.call_args[0][8], 'NA')  # external_id
        self.assertEqual(mock_audit.call_args[0][9], 'CMS')  # event_details
        # self.assertEqual(mock_audit.call_args[0][10], 'Saved to DB')  # status

    @mock.patch('audit_client.api.audit.init')
    @mock.patch('audit_client.api.audit.audit')
    def test_audit_service_with_requester(self, mock_audit, mock_init):
        resp = utils.audit_trail('create customer', '1234',
                                 {'X-RANGER-Client': 'Fred',
                                  'X-RANGER-Requester': 'Req04'}, '5678')
        self.assertEqual(mock_audit.call_args[0][1], 'Fred')  # application_id
        self.assertEqual(mock_audit.call_args[0][2], '1234')  # tracking_id
        self.assertEqual(mock_audit.call_args[0][3], '1234')  # transaction_id
        self.assertEqual(mock_audit.call_args[0][4], 'create customer')  # transaction_type
        self.assertEqual(mock_audit.call_args[0][5], '5678')  # resource_id
        # self.assertEqual(mock_audit.call_args[0][6], 'cms')  # service
        self.assertEqual(mock_audit.call_args[0][7], 'Req04')  # user_id
        self.assertEqual(mock_audit.call_args[0][8], 'NA')  # external_id
        self.assertEqual(mock_audit.call_args[0][9], 'CMS')  # event_details
        # self.assertEqual(mock_audit.call_args[0][10], 'Saved to DB')  # status

    def test_set_utils_conf(self):
        utils.set_utils_conf('test')
        self.assertEqual(utils.conf, 'test')

    def test_check_conf_initialization(self):
        utils.set_utils_conf(None)
        self.assertRaises(AssertionError, utils._check_conf_initialization)

    @mock.patch('requests.post')
    def test_create_existing_uuid(self, mock_post):
        uuid = '987654321'
        mock_post.return_value = self.respond({'uuid': uuid}, 200)
        returned_uuid = utils.create_existing_uuid(uuid)
        self.assertEqual(returned_uuid, uuid)

    @mock.patch('requests.post')
    def test_create_existing_uuid_with_exception(self, mock_post):
        mock_post.side_effect = Exception('boom')
        uuid = '987654321'
        returned_uuid = utils.create_existing_uuid(uuid)
        self.assertEqual(returned_uuid, None)

    @mock.patch('requests.post')
    def test_create_existing_uuid_with_400(self, mock_post):
        uuid = '987654321'
        mock_post.return_value = self.respond({'uuid': uuid}, 400)
        self.assertRaises(TypeError, utils.create_existing_uuid, uuid)

    @mock.patch('pecan.conf')
    def test_report_config(self, mock_conf):
        expected_value = pprint.pformat(mock_conf.to_dict(), indent=4)
        returned_value = utils.report_config(mock_conf)
        self.assertEqual(expected_value, returned_value)

    @mock.patch('pecan.conf')
    def test_report_config_with_log_write(self, mock_conf):
        expected_value = pprint.pformat(mock_conf.to_dict(), indent=4)
        returned_value = utils.report_config(mock_conf, True)
        self.assertEqual(expected_value, returned_value)

    @mock.patch('requests.get')
    def test_get_resource_status_sanity(self, mock_get):
        my_response = mock.MagicMock()
        my_response.status_code = 200
        my_response.json.return_value = 'test'
        mock_get.return_value = my_response
        result = utils.get_resource_status('A')
        self.assertEqual(result, 'test')

    @mock.patch('requests.get', side_effect=ValueError())
    def test_get_resource_status_get_failed(self, mock_get):
        self.assertIsNone(utils.get_resource_status('A'))

    @mock.patch('requests.get')
    def test_get_resource_status_invalid_response(self, mock_get):
        my_response = mock.MagicMock()
        my_response.status_code = 404
        mock_get.return_value = my_response
        self.assertIsNone(utils.get_resource_status('A'))
