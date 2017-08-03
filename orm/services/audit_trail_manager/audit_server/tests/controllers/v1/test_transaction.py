"""test_transaction module."""


from audit_server.controllers.v1.transaction import QueryResult
from audit_server.model.transaction import Model as TransactionModel
from audit_server.model.transaction_query_result import \
    Model as TransactionQueryResultModel
from audit_server.services import transaction as transaction_service
from audit_server.tests.controllers.v1.functional_test import FunctionalTest
from mock import patch


class Test(FunctionalTest):
    """test transaction class."""

    transaction_model = TransactionModel(timestamp=111, user_id="user_id_1",
                                         application_id="application_id_1",
                                         tracking_id="tracking_id_1",
                                         external_id="external_id_1",
                                         transaction_id="transaction_id_1",
                                         transaction_type="transaction_type_1",
                                         event_details="event_details_1",
                                         resource_id="resource_id_1",
                                         service_name="service_name_1")

    @patch.object(transaction_service, 'get_transactions',
                  return_value=TransactionQueryResultModel(
                      [transaction_model]))
    def test_get_all(self, mock_get_transactions):
        """test that get_one returns an appropriate json result."""
        url = "/audit/transaction?q.timestamp_from=1111&q.timestamp_to=5555&" \
              "q.user_id=user1&q.application_id=SSP&limit=15&marker=1"
        output = self.get_json(url)
        returned_transactions = output['transactions']
        self.assertIsNotNone(returned_transactions)
        self.assertEqual(len(returned_transactions), 1)
        transaction = returned_transactions[0]
        self._assert_returned_transaction(transaction)

    @patch.object(transaction_service, 'get_transactions',
                  return_value=TransactionQueryResultModel(
                      [transaction_model]))
    def test_get_all_with_empty_query(self, mock_get_transactions):
        """Test that get_one accepts an empty query and returns a response."""
        url = "/audit/transaction?limit=15&marker=1"
        output = self.get_json(url)
        returned_transactions = output['transactions']
        self.assertIsNotNone(returned_transactions)
        self.assertEqual(len(returned_transactions), 1)
        transaction = returned_transactions[0]
        self._assert_returned_transaction(transaction)

    @patch.object(transaction_service, 'add_transaction')
    def test_post(self, mock_transaction_service):
        """Test that post is executed with no exceptions."""
        url = "/audit/transaction"
        body = {
            "timestamp": 111,
            "user_id": "user_1",
            "application_id": "application_id_1",
            "tracking_id": "tracking_id_1",
            "external_id": "external_id_1",
            "transaction_id": "transaction_id_1",
            "transaction_type": "transaction_type_1",
            "event_details": "event_details_1",
            "resource_id": "resource_id_1",
            "service_name": "service_name_1"
        }
        self.post_json(url, body)

    def test_init_QueryResult(self):
        """test the init method."""
        QueryResult(**{"prop1": "value1", "prop2": "value2"})

    def _assert_returned_transaction(self, transaction):
        """Check the returned trasaction."""
        self.assertEqual(transaction['timestamp'],
                         self.transaction_model.timestamp)
        self.assertEqual(transaction['user_id'],
                         self.transaction_model.user_id)
        self.assertEqual(transaction['application_id'],
                         self.transaction_model.application_id)
        self.assertEqual(transaction['tracking_id'],
                         self.transaction_model.tracking_id)
        self.assertEqual(transaction['external_id'],
                         self.transaction_model.external_id)
        self.assertEqual(transaction['transaction_id'],
                         self.transaction_model.transaction_id)
        self.assertEqual(transaction['transaction_type'],
                         self.transaction_model.transaction_type)
        self.assertEqual(transaction['event_details'],
                         self.transaction_model.event_details)
        self.assertEqual(transaction['resource_id'],
                         self.transaction_model.resource_id)
        self.assertEqual(transaction['service_name'],
                         self.transaction_model.service_name)
