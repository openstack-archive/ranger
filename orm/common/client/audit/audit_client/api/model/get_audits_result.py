"""get_audit_result module."""


class AuditsResult(object):
    """AuditResult class."""

    def __init__(self, transactions):
        """init method."""
        self.transactions = transactions

    def __str__(self):
        """string representation of the object."""
        return "AuditsResult[ " \
               "transactions: {}]".format(self.transactions)
