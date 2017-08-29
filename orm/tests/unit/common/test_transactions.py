"""test transactions module."""

import unittest

from orm.common.client.audit.audit_client.api.model.transaction import Transaction


class Test(unittest.TestCase):
    """test transactions class."""

    def test_init_AuditsResult(self):
        """test init method."""
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
        transaction = Transaction(timestamp, user_id, application_id,
                                  tracking_id, external_id, transaction_id,
                                  transaction_type, event_details,
                                  resource_id, service_name)
        self.assertEqual(str(transaction), "Transaction:["
                                           "timestamp={}, "
                                           "user_id={}, "
                                           "application_id={}, "
                                           "tracking_id={}, "
                                           "external_id={}, "
                                           "transaction_id={}, "
                                           "transaction_type={}, "
                                           "event_details={}, "
                                           "resource_id={}, "
                                           "service_name={}]".format(
            timestamp,
            user_id,
            application_id,
            tracking_id,
            external_id,
            transaction_id,
            transaction_type,
            event_details,
            resource_id,
            service_name))

        self.assertEqual(transaction.__repr__(), "Transaction:["
                                                 "timestamp={}, "
                                                 "user_id={}, "
                                                 "application_id={}, "
                                                 "tracking_id={}, "
                                                 "external_id={}, "
                                                 "transaction_id={}, "
                                                 "transaction_type={}, "
                                                 "event_details={}, "
                                                 "resource_id={}, "
                                                 "service_name={}]".format(
            timestamp,
            user_id,
            application_id,
            tracking_id,
            external_id,
            transaction_id,
            transaction_type,
            event_details,
            resource_id,
            service_name))
