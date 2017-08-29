"""test_audit module."""

import json
import threading
import unittest
import urllib2

from orm.common.client.audit.audit_client.api import audit
from orm.common.client.audit.audit_client.api.exceptions.audit_exception import AuditException

from mock import patch


class Test(unittest.TestCase):
    """test audit class."""

    data = {
        'transactions': [
            {
                'timestamp': 111,
                'user_id': 'user_id_1',
                'application_id': 'application_id_1',
                'tracking_id': 'tracking_id_1',
                'external_id': 'external_id_1',
                'transaction_id': 'transaction_id_1',
                'transaction_type': 'transaction_type_1',
                'event_details': 'event_details_1',
                'resource_id': "resource_id_1",
                'service_name': "service_name_1"
            }, {
                'timestamp': 111,
                'user_id': 'user_id_2',
                'application_id': 'application_id_2',
                'tracking_id': 'tracking_id_2',
                'external_id': 'external_id_2',
                'transaction_id': 'transaction_id_2',
                'transaction_type': 'transaction_type_2',
                'event_details': 'event_details_2',
                'resource_id': "resource_id_2",
                'service_name': "service_name_3"
            }, {
                'timestamp': 111,
                'user_id': 'user_id_3',
                'application_id': 'application_id_3',
                'tracking_id': 'tracking_id_3',
                'external_id': 'external_id_3',
                'transaction_id': 'transaction_id_3',
                'transaction_type': 'transaction_type_3',
                'event_details': 'event_details_3',
                'resource_id': "resource_id_3",
                'service_name': "service_name_3"
            }
        ]
    }

    def test_init(self):
        """test init method.

        test that init doesn't throw and exeception/error
        and that the gloabl variables are set correctly
        """
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 5
        time_wait_between_retries = 10
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        self.assertEqual(audit.config['AUDIT_SERVER_URL'], audit_server_url)
        self.assertEqual(audit.config['NUM_OF_SEND_RETRIES'],
                         num_of_send_retries)
        self.assertEqual(audit.config['TIME_WAIT_BETWEEN_RETRIES'],
                         time_wait_between_retries)

    #
    def test_init_with_audit_server_url_empty(self):
        """test that init throws an exception when audit_server_url is None."""
        audit_server_url = None
        num_of_send_retries = 5
        time_wait_between_retries = 10
        self.assertRaises(AuditException, audit.init, audit_server_url,
                          num_of_send_retries, time_wait_between_retries)

    def test_init_with_num_of_send_retries_empty(self):
        """test init method.

        test that init throws an exception when num_of_send_retries is None
        """
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = None
        time_wait_between_retries = 10
        self.assertRaises(AuditException, audit.init, audit_server_url,
                          num_of_send_retries, time_wait_between_retries)

    def test_init_with_time_wait_between_retries_empty(self):
        """test init method.

        Test that init throws an exception when
        time_wait_between_retries is None.
        """
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 5
        time_wait_between_retries = None
        self.assertRaises(AuditException, audit.init, audit_server_url,
                          num_of_send_retries, time_wait_between_retries)

    def test_validate(self):
        """test validate method.

        test that _validate doesn't throw and exception when all variables
        are populated
        """
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 5
        time_wait_between_retries = 10
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        audit._validate()

    def test_validate_with_audit_server_url_empty(self):
        """test validate with audit_server_url.

        test that _validate throw and exception when AUDIT_SERVER_URL
        is None.
        """
        audit.config['AUDIT_SERVER_URL'] = None
        audit.config['NUM_OF_SEND_RETRIES'] = 5
        audit.config['TIME_WAIT_BETWEEN_RETRIES'] = 10
        self.assertRaises(AuditException, audit._validate)

    def test_validate_with_num_of_send_retries_empty(self):
        """test validate with num of send_retries_empty.

        test that _validate throw and exception when NUM_OF_SEND_RETRIES
        is None
        """
        audit.config['AUDIT_SERVER_URL'] = "audit_server_url_1"
        audit.config['NUM_OF_SEND_RETRIES'] = None
        audit.config['TIME_WAIT_BETWEEN_RETRIES'] = 10
        self.assertRaises(AuditException, audit._validate)

    def test_validate_with_time_wait_between_retries_empty(self):
        """test validate with ime_wait_between_retries_empty.

        test that _validate throw and exception when
        TIME_WAIT_BETWEEN_RETRIES is None
        """
        audit.config['AUDIT_SERVER_URL'] = "audit_server_url_1"
        audit.config['NUM_OF_SEND_RETRIES'] = 5
        audit.config['TIME_WAIT_BETWEEN_RETRIES'] = None
        self.assertRaises(AuditException, audit._validate)

    @patch.object(urllib2, 'urlopen')
    @patch.object(json, 'load', return_value=data)
    def test_get_audits(self, mock_urlopen, mock_load):
        """test get_audits."""
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 5
        time_wait_between_retries = 10
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        result = audit.get_audits()
        self.assertEqual(len(result.transactions), 3)

    @patch.object(urllib2, 'urlopen')
    @patch.object(json, 'load')
    def test_audit_thread(self, mock_urlopen, mock_load):
        """Test audit_thread is executed with no exceptions."""
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 5
        time_wait_between_retries = 10
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        timestamp = 111
        application_id = 'application_id_1'
        tracking_id = 'tracking_id_1'
        transaction_id = 'transaction_id_1'
        transaction_type = 'transaction_type_1'
        user_id = 'user_id_1'
        external_id = 'external_id_1'
        event_details = 'event_details_1'
        resource_id = 'resource_id_1'
        service_name = 'service_name_1'
        audit._audit_thread(timestamp, application_id, tracking_id,
                            transaction_id, transaction_type,
                            resource_id, service_name, user_id, external_id,
                            event_details)

    @patch.object(urllib2, 'urlopen')
    @patch.object(json, 'load')
    def test_post_data(self, mock_urlopen, mock_load):
        """test that post_data is executed with no exceptions."""
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 5
        time_wait_between_retries = 10
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        audit._post_data(None)

    @patch.object(urllib2, 'urlopen', side_effect=Exception)
    @patch.object(json, 'load')
    def test_post_data_with_retry_exception(self, mock_urlopen, mock_load):
        """test post data with retry_exception.

        test that post_data throws an exception when trying to send
        a data for num_of_send_retries
        """
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 1
        time_wait_between_retries = 1
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        self.assertRaises(AuditException, audit._post_data, None)

    def test_build_query(self):
        """test that build_query is exceuted with no exception."""
        query = "query_1"
        arg_name = "arg_1"
        arg_value = "arg_value_1"
        expected_query = query + "%s=%s&" % (arg_name, arg_value)
        returned_query = audit._build_query(query, arg_name, arg_value)
        self.assertEqual(returned_query, expected_query)

    def test_build_query_with_empty_arg_value(self):
        """test build query with empty_arg_value.

        test that build_query throws an exception when called
        with empty arg_value.
        """
        query = "query_1"
        arg_name = "arg_1"
        arg_value = None
        expected_query = query
        returned_query = audit._build_query(query, arg_name, arg_value)
        self.assertEqual(returned_query, expected_query)

    @patch.object(threading, 'Thread')
    def test_audit(self, mock_thread):
        """test that audit is exceuted with no exception."""
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 1
        time_wait_between_retries = 1
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        timestamp = 111
        application_id = 'application_id_1'
        tracking_id = 'tracking_id_1'
        transaction_id = 'transaction_id_1'
        transaction_type = 'transaction_type_1'
        user_id = 'user_id_1'
        external_id = 'external_id_1'
        event_details = 'event_details_1'
        resource_id = 'resource_id_1'
        service_name = 'service_name_1'
        audit.audit(timestamp, application_id, tracking_id, transaction_id,
                    transaction_type, resource_id, service_name, user_id,
                    external_id, event_details)

    def test_get_data(self):
        """test get data."""
        audit_server_url = "audit_server_url_1"
        num_of_send_retries = 1
        time_wait_between_retries = 1
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        query = "query1"
        self.assertRaises(AuditException, audit._get_data, query)
