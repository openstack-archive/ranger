"""test_transaction module."""

import unittest

from mock import patch

from audit_server.model.transaction import Model as TransactionModel
from audit_server.model.transaction_query import Model as TransactionQuery
from audit_server.services import transaction as TransactionService
from audit_server.storage import factory


class Test(unittest.TestCase):
    """test transaction class."""

    @patch.object(factory, 'get_transaction_connection')
    def test_add_transaction(self, mock_factory):
        """test that add_transaction doesn't throws any exception."""
        timestamp = 111
        user_id = "user_id_1"
        application_id = "application_id_1"
        tracking_id = "tracking_id_1"
        external_id = "external_id_1"
        transaction_id = "transaction_id_1"
        transaction_type = "transaction_type_1"
        event_details = "event_details_1"
        resource_id = "resource_id_1"
        service_name = "service_name_1"
        transaction = TransactionModel(timestamp, user_id, application_id,
                                       tracking_id, external_id,
                                       transaction_id, transaction_type,
                                       event_details, resource_id,
                                       service_name)
        TransactionService.add_transaction(transaction)

    @patch.object(factory, 'get_transaction_connection')
    def test_get_transaction(query, mock_factory):
        """test that get_transaction doesn't throws any exception."""
        timestamp_from = 111
        timestamp_to = 555
        user_id = "user_id_1"
        application_id = "application_id_1"
        tracking_id = "tracking_id_1"
        external_id = "external_id_1"
        transaction_id = "transaction_id_1"
        transaction_type = "transaction_type_1"
        event_details = "event_details_1"
        resource_id = "resource_id_1"
        service_name = "service_name_1"
        query = TransactionQuery(timestamp_from, timestamp_to, user_id,
                                 application_id, tracking_id, external_id,
                                 transaction_id, transaction_type,
                                 event_details, resource_id, service_name)
        limit = 10
        marker = 1
        TransactionService.get_transactions(query, limit, marker)
