"""test_transaction_query_result module."""


import unittest

from orm.services.audit_trail_manager.audit_server.model.transaction_query_result import \
    Model as TransactionQueryResultModel


class Test(unittest.TestCase):
    """test transaction query result class."""

    def test_str(self):
        """test str method."""
        transactions = []
        model = TransactionQueryResultModel(transactions)
        self.assertEqual(str(model),
                         "TransactionQueryResult:[ transactions={}]".format(
                             transactions))
