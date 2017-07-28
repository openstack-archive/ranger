"""test_get_audits_result module."""

from audit_client.api.model.get_audits_result import AuditsResult
import unittest


class Test(unittest.TestCase):
    """test get audits result class."""

    def test_init_AuditsResult(self):
        """test init method."""
        transactions = []
        audit_result = AuditsResult(transactions)
        self.assertEqual(str(audit_result),
                         "AuditsResult[ transactions: {}]".format(
                             transactions))
