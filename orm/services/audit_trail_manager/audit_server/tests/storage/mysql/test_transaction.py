"""test_transaction module."""

import unittest

from audit_server.model.transaction import Model as TransactionModel
from audit_server.model.transaction_query import Model as TransactionQueryModel
from audit_server.storage.mysql.transaction import Connection, Record
from mock import patch
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker


class Test(unittest.TestCase):
    """test transaction class."""

    transaction = TransactionModel(timestamp=111, user_id="user_id_1",
                                   application_id="application_id_1",
                                   tracking_id="tracking_id_1",
                                   external_id="external_id_1",
                                   transaction_id="transaction_id_1",
                                   transaction_type="transaction_type_1",
                                   event_details="event_details_1",
                                   resource_id="resource_id_1",
                                   service_name="service_name_1")

    transaction_query = TransactionQueryModel(111, 222, "user_id1",
                                              "application_id1",
                                              "tracking_id1",
                                              "external_id1",
                                              "transaction_id1",
                                              "transaction_type1",
                                              "event_details1",
                                              "resource_id_1",
                                              "service_name_1")

    @patch.object(create_engine, '__init__')
    @patch.object(sessionmaker, '__init__')
    def setUp(self, mock_engine, mock_sessionmaker):
        """setup method."""
        self.mock_engine = mock_engine
        self.mock_sessionmaker = mock_sessionmaker
        self.conn = object.__new__(Connection)
        self.conn._engine = self.mock_engine
        self.conn._session_maker = self.mock_sessionmaker

    def test_add_record(self):
        """test add record.

        test that no exception/error is thrown when calling the
        add_record execution.
        """
        self.conn.add_record(self.transaction)

    def test_add_record_duplicate_entry(self):
        """test duplicate entries to add record.

        test that when session.add throws Duplicate Entry exception,
        no expcetion is thrown back.
        """
        side_effect = IntegrityError(None, None, None, None)
        side_effect.message = "Duplicate entry"
        mock_session = self.mock_sessionmaker.return_value.__call__
        mock_add = mock_session.im_self.add
        mock_add.side_effect = side_effect
        self.conn.add_record(self.transaction)

    def test_add_record_integrity_entry(self):
        """test add record that throws integrity error.

        test that when session.add throws a different exception
        than Duplicate Entry it will be rasied up.
        """
        side_effect = IntegrityError(None, None, None, None)
        side_effect.message = "Some other integrity error"
        mock_session = self.mock_sessionmaker.return_value.__call__
        mock_add = mock_session.im_self.add
        mock_add.side_effect = IntegrityError("Some other integrity error",
                                              None, None, None)
        self.assertRaises(IntegrityError, self.conn.add_record,
                          self.transaction)

    def test_get_records(self):
        """test get records.

        test that get_records returns a list and that
        no exception/error is thrown.
        """
        # mock record
        record = Record()
        record.id = 1
        record.timestamp = 111
        record.user_id = "user_id1"
        record.application_id = "application_id1"
        record.tracking_id = "tracking_id1"
        record.external_id = "external_id1"
        record.transaction_id = "transaction_id1"
        record.transaction_type = "transaction_type1"
        record.event_details = "event_details1"

        mock_returned_records = [record]

        # The transaction query above will result in the following method call:
        # EngineFacade().get_session().query().filter().filter().filter().
        # filter().filter().filter().filter().filter().filter().filter().
        # order_by().limit() Therefore we will need to mock the entire
        # call tree in order to set the required returned value
        mock_session = self.mock_sessionmaker.return_value.__call__
        mock_query = mock_session.im_self.query
        mock_filter = mock_query.return_value.filter
        for key in range(len(self.transaction_query.__dict__.keys()) - 1):
            mock_filter = mock_filter.return_value.filter
        mock_order_by = mock_filter.return_value.order_by
        mock_limit = mock_order_by.return_value.limit
        mock_all = mock_limit.return_value.all
        mock_all.return_value = mock_returned_records

        returned_records = self.conn.get_records(self.transaction_query)

        self.assertIsNotNone(returned_records)
        self.assertIsInstance(returned_records, list)
        # Check that the list is not empty
        self.assertTrue(returned_records)
        # Compare the return record value with the expected value
        self.assertTrue(len(returned_records), len(mock_returned_records))
        self.assertEqual(returned_records[0].timestamp,
                         mock_returned_records[0].timestamp)
        self.assertEqual(returned_records[0].user_id,
                         mock_returned_records[0].user_id)
        self.assertEqual(returned_records[0].application_id,
                         mock_returned_records[0].application_id)
        self.assertEqual(returned_records[0].tracking_id,
                         mock_returned_records[0].tracking_id)
        self.assertEqual(returned_records[0].external_id,
                         mock_returned_records[0].external_id)
        self.assertEqual(returned_records[0].transaction_id,
                         mock_returned_records[0].transaction_id)
        self.assertEqual(returned_records[0].transaction_type,
                         mock_returned_records[0].transaction_type)
        self.assertEqual(returned_records[0].event_details,
                         mock_returned_records[0].event_details)

    def test_get_records_returns_none(self):
        """test get records return none.

        Test get_records will return empty list when session
        returns empty list.
        """
        mock_session = self.mock_engine.return_value.get_session
        mock_query = mock_session.return_value.query
        mock_filter_by = mock_query.return_value.filter_by
        mock_order_by = mock_filter_by.return_value.order_by
        mock_first = mock_order_by.return_value.first
        mock_first.return_value = []
        returned_records = self.conn.get_records(self.transaction_query)
        self.assertIsNotNone(returned_records)
        self.assertIsInstance(returned_records, list)
        # Check that the list is empty
        self.assertTrue(not returned_records)

    def test_get_records_with_empty_query(self):
        """test get record with empty query.

        test get_records with empty query will not throw an exception
        and will returns a result.
        """
        transaction_query = None
        self.conn.get_records(transaction_query)

    def test_add_filter(self):
        """test that add_filter is executed with no exceptions/error."""
        marker = 5
        session = self.mock_engine.get_session()
        records = session.query(Record)
        records = self.conn._add_filter(records, self.transaction_query,
                                        marker)

    def test_add_filter_with_timestamp_empty(self):
        """test add filter with empty timestamp.

        test that add_filter is executed with no exceptions/error
        when timestamp_from and timestamp_to are empty.
        """
        timestamp_from = None
        timestamp_to = None
        user_id = "user_id_1"
        application_id = "application_id_1"
        tracking_id = "tracking_id_1"
        external_id = "external_id_1"
        transaction_id = "transaction_id_1"
        transaction_type = "transaction_type_1"
        event_details = "event_details_1"
        resource_id = "resource_id_1"
        service_name = "service_name_1"
        query = TransactionQueryModel(timestamp_from, timestamp_to, user_id,
                                      application_id, tracking_id,
                                      external_id, transaction_id,
                                      transaction_type, event_details,
                                      resource_id, service_name)
        marker = 5
        session = self.mock_engine.get_session()
        records = session.query(Record)
        records = self.conn._add_filter(records, query, marker)

    def test_add_filter_eq(self):
        """test that add_filter_eq will not throw an exception."""
        session = self.mock_engine.get_session()
        records = session.query(Record)
        key = "key1"
        value = "value1"
        records = self.conn._add_filter_eq(records, key, value)

    def test_add_filter_eq_with_empty_value(self):
        """test add filter with empty value.

        test that add_filter_eq will not throw an exception
        when value is None.
        """
        session = self.mock_engine.get_session()
        records = session.query(Record)
        key = "key1"
        value = None
        records = self.conn._add_filter_eq(records, key, value)
