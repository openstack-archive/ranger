"""Unittest module for mysql.region_resource_id_status."""
import time
import unittest

import mock
from mock import patch
from rds.storage.mysql import region_resource_id_status


class RecordMock(object):
    def __init__(self, record=None):
        self._record = record
        self.timestamp = 0
        self.status = "Submitted"
        self.err_msg = "test"
        self.region = "1"
        self.transaction_id = "2"
        self.resource_id = "3"
        self.ord_notifier = "4"
        self.err_code = 1
        self.operation = "create"
        self.resource_extra_metadata = None

    def first(self):
        return self._record

    def delete(self):
        return


class MyFacade(object):
    """Mock EngineFacade class."""

    def __init__(self, dup_entry=False,
                 record_exist=False,
                 is_get_records=False):
        """Initialize the object."""
        self._is_dup_entry = dup_entry
        self._is_record_exist = record_exist
        self._is_get_records = is_get_records

    def get_session(self):

        session = mock.MagicMock()
        if self._is_dup_entry:
            dup_ent = region_resource_id_status.oslo_db.exception.DBDuplicateEntry
            session.add = mock.MagicMock(side_effect=dup_ent('test'))

        records = None
        my_record = RecordMock()
        if self._is_record_exist:
            my_record = RecordMock(mock.MagicMock())
            records = [RecordMock()]

        my_filter = mock.MagicMock()
        if not self._is_get_records:
            my_filter.filter_by = mock.MagicMock(return_value=my_record)
        else:
            my_filter.filter_by = mock.MagicMock(return_value=records)

        session.query = mock.MagicMock(return_value=my_filter)

        return session


class MysqlRegionResourceIdStatusTest(unittest.TestCase):
    """Main test case of this module."""

    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(False, True))
    def test_add_update_status_record_record_exist_sanity(self, mock_db_session):
        """Test that no exception is raised when calling add_update_status_record.
        where record exist
        """
        my_connection = region_resource_id_status.Connection('url')
        my_connection.add_update_status_record('timestamp',
                                               'region',
                                               'status',
                                               'transaction_id',
                                               'resource_id',
                                               'ord_notifier',
                                               'err_msg',
                                               'err_code',
                                               {"checksum": "1",
                                                "virtual_size": "2",
                                                "size": "3"})

    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade())
    def test_add_update_status_record_record_not_exist_sanity(self, mock_db_session):
        """Test that no exception is raised when calling add_update_status_record.
        where record does not exist
        """
        my_connection = region_resource_id_status.Connection('url')
        my_connection.add_update_status_record('timestamp',
                                               'region',
                                               'status',
                                               'transaction_id',
                                               'resource_id',
                                               'ord_notifier',
                                               'err_msg',
                                               'create',
                                               'err_code')

    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(True, False))
    def test_add_update_status_record_duplicate_entry(self, mock_db_session):
        """No exception is raised when trying to add a duplicate entry."""
        my_connection = region_resource_id_status.Connection('url')
        my_connection.add_update_status_record('timestamp',
                                               'region',
                                               'status',
                                               'transaction_id',
                                               'resource_id',
                                               'ord_notifier',
                                               'err_msg',
                                               'delete',
                                               'err_code')

    @mock.patch.object(region_resource_id_status, 'StatusModel')
    @patch.object(region_resource_id_status.Connection,
                  'get_timstamp_pair',
                  return_value=(1, 2))
    @mock.patch.object(region_resource_id_status, 'Model')
    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(False, False, True))
    def test_get_records_by_filter_args_no_records(self, mock_db_session,
                                                   mock_get_timestamp,
                                                   mock_model,
                                                   mock_statusmodel):
        """Test that the function returns None when it got no records."""
        my_connection = region_resource_id_status.Connection('url')
        self.assertIsNone(my_connection.get_records_by_filter_args())

    @mock.patch.object(region_resource_id_status, 'StatusModel')
    @patch.object(region_resource_id_status.Connection,
                  'get_timstamp_pair',
                  return_value=(1, 2))
    @mock.patch.object(region_resource_id_status, 'Model')
    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(False, True, True))
    def test_get_records_by_filter_args_with_records(self,
                                                     mock_db_session,
                                                     mock_get_timestamp,
                                                     mock_model,
                                                     mock_statusmodel):
        """Test that the function returns None when it got records."""
        my_connection = region_resource_id_status.Connection('url')
        my_connection.get_records_by_filter_args()

    @mock.patch.object(region_resource_id_status, 'StatusModel')
    @patch.object(region_resource_id_status.Connection,
                  'get_timstamp_pair',
                  return_value=(1, 2))
    @mock.patch.object(region_resource_id_status, 'Model')
    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(False, False, True))
    def test_get_records_by_resource_id_sanity(self, mock_db_session,
                                               mock_get_timestamp,
                                               mock_model,
                                               mock_statusmodel):
        """No exception is raised when calling get_records_by_resource_id."""
        my_connection = region_resource_id_status.Connection('url')
        my_connection.get_records_by_resource_id('test')

    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade())
    @patch.object(time, 'time', return_value=80)
    @mock.patch.object(region_resource_id_status, 'conf')
    def test_get_timstamp_pair_sanity(self, db_session, time_mock, conf_mock):
        """Test get_timestamp_pair"""
        conf_mock.region_resource_id_status.max_interval_time.default = 1
        my_connection = region_resource_id_status.Connection('url')
        (timestamp, ref_timestamp) = my_connection.get_timstamp_pair()
        self.assertEqual(timestamp, 80000)

    @mock.patch.object(region_resource_id_status, 'StatusModel')
    @patch.object(region_resource_id_status.Connection,
                  'get_timstamp_pair',
                  return_value=(1, 2))
    @mock.patch.object(region_resource_id_status, 'Model')
    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(False, False, True))
    def test_get_records_by_resource_id_and_status_no_records(self, mock_db_session,
                                                              mock_get_timestamp,
                                                              mock_model,
                                                              mock_statusmodel):
        """Test that the function returns None when it got no records."""
        my_connection = region_resource_id_status.Connection('url')
        self.assertIsNone(my_connection.get_records_by_resource_id_and_status('1', '2'))

    @mock.patch.object(region_resource_id_status, 'StatusModel')
    @patch.object(region_resource_id_status.Connection, 'get_timstamp_pair',
                  return_value=(1, 2))
    @mock.patch.object(region_resource_id_status, 'Model')
    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(False, True, True))
    def test_get_records_by_resource_id_and_status_sanity(self, mock_db_session,
                                                          mock_get_timestamp,
                                                          mock_model,
                                                          mock_statusmodel):
        my_connection = region_resource_id_status.Connection('url')
        my_connection.get_records_by_resource_id_and_status('1', '2')

    @mock.patch.object(region_resource_id_status, 'StatusModel')
    @patch.object(region_resource_id_status.Connection, 'get_timstamp_pair',
                  return_value=(1, 0))
    @mock.patch.object(region_resource_id_status, 'Model')
    @mock.patch.object(region_resource_id_status.db_session, 'EngineFacade',
                       return_value=MyFacade(False, True, True))
    def test_get_records_by_resource_id_and_status_with_records(self, mock_db_session,
                                                                mock_get_timestamp,
                                                                mock_model,
                                                                mock_statusmodel):
        my_connection = region_resource_id_status.Connection('url')
        my_connection.get_records_by_resource_id_and_status('1', '2')
