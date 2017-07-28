"""transaction_query model module."""


class Model(object):
    """transaction query model."""

    def __init__(self, timestamp_from, timestamp_to, user_id, application_id,
                 tracking_id, external_id, transaction_id, transaction_type,
                 event_details, resource_id, service_name):
        """init method."""
        self.timestamp_from = timestamp_from
        self.timestamp_to = timestamp_to
        self.user_id = user_id
        self.application_id = application_id
        self.tracking_id = tracking_id
        self.external_id = external_id
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.event_details = event_details
        self.resource_id = resource_id
        self.service_name = service_name

    def __str__(self):
        """return a string representation of the object."""
        return "Transaction:[ " \
               "timestamp_from={}, " \
               "timestamp_to={}" \
               "user_id={}, " \
               "application_id={}, " \
               "tracking_id={}, " \
               "external_id={}, " \
               "transaction_id={}," \
               "transaction_type={}, " \
               "event_details={}, " \
               "resource_id={}," \
               "service_name={}]".format(self.timestamp_from,
                                         self.timestamp_to,
                                         self.user_id,
                                         self.application_id,
                                         self.tracking_id,
                                         self.external_id,
                                         self.transaction_id,
                                         self.transaction_type,
                                         self.event_details,
                                         self.resource_id,
                                         self.service_name)
