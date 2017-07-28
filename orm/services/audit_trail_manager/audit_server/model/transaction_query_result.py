"""transaction_query_result model module."""


class Model(object):
    """transaction query result model."""

    def __init__(self, transactions):
        """init method."""
        self.transactions = transactions

    def __str__(self):
        """return a string representation of the object."""
        return "TransactionQueryResult:[ " \
               "transactions={}]".format(self.transactions)
