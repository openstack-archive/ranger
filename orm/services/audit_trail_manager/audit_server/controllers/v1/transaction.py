"""transaction controller module."""

from audit_server.model.transaction import Model as TransactionModel
from audit_server.model.transaction_query import Model as QueryModel
from audit_server.services import transaction as transaction_service
import base
import logging
from pecan import rest
import wsme
from wsme import types as wtypes
from wsmeext.pecan import wsexpose


logger = logging.getLogger(__name__)


class Transaction(base.Base):
    """transaction type."""

    timestamp = wsme.wsattr(long, mandatory=True)
    user_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    application_id = wsme.wsattr(wtypes.text, mandatory=True)
    tracking_id = wsme.wsattr(wtypes.text, mandatory=True)
    external_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    transaction_id = wsme.wsattr(wtypes.text, mandatory=True)
    transaction_type = wsme.wsattr(wtypes.text, mandatory=True)
    event_details = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    resource_id = wsme.wsattr(wtypes.text, mandatory=True)
    service_name = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, **kwargs):
        """init method."""
        super(Transaction, self).__init__(**kwargs)

    def to_model(self):
        """transform the Transaction  to a TransactionModel."""
        return TransactionModel(self.timestamp,
                                self.user_id,
                                self.application_id,
                                self.tracking_id,
                                self.external_id,
                                self.transaction_id,
                                self.transaction_type,
                                self.event_details,
                                self.resource_id,
                                self.service_name)

    def __str__(self):
        """return a string representation of the object."""
        return "Transaction:[ " \
               "timestamp={}, " \
               "user_id={}, " \
               "application_id={}, " \
               "tracking_id={}, " \
               "external_id={}, " \
               "transaction_id={}," \
               "transaction_type={}, " \
               "event_details={}, " \
               "resource_id={}," \
               "service_name={}]".format(self.timestamp,
                                         self.user_id,
                                         self.application_id,
                                         self.tracking_id,
                                         self.external_id,
                                         self.transaction_id,
                                         self.transaction_type,
                                         self.event_details,
                                         self.resource_id,
                                         self.service_name)


class Query(base.Base):
    """query type."""

    timestamp_from = wsme.wsattr(long, mandatory=False, default=None)
    timestamp_to = wsme.wsattr(long, mandatory=False, default=None)
    user_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    application_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    tracking_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    external_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    transaction_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    transaction_type = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    event_details = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    resource_id = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    service_name = wsme.wsattr(wtypes.text, mandatory=False, default=None)

    def __init__(self, **kwargs):
        """init method."""
        super(Query, self).__init__(**kwargs)

    def to_model(self):
        """transform the Query to a QueryModel."""
        return QueryModel(self.timestamp_from,
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

    def __str__(self):
        """return a string representation of the object."""
        return "TransactionQuery:[ " \
               "timestamp_from={}, " \
               "timestamp_to={}, " \
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


class QueryResult(base.Base):
    """query result type."""

    transactions = wsme.wsattr([Transaction], mandatory=False, default=None)

    def __init__(self, **kwargs):
        """"init method."""
        super(QueryResult, self).__init__(**kwargs)


class TransactionController(rest.RestController):
    """Transaction Audit controller."""

    @wsexpose(QueryResult, Query, int, str, rest_content_types='json')
    def get_all(self, q=None, limit=10, marker=None):
        """get all transactions that meet the given query.

        :param q: the query to use in order to search for relevant.
        transactions.
        :param limit: the maximun number of transactions to return.
        :param marker: a place order for pagination (not implemented yet).

        Example of usage:
        http://127.0.0.1:8777/v1/audit/transaction?q.timestamp_from=1111&q.
        timestamp_to=5555&q.user_id=user1&q.application_id=SSP&limit=15&
        marker=1
        """
        logger.debug("Getting audit records...start")
        logger.info(
            "Getting audit records for the query:[{}]...start".format(q))
        model = None
        if q is not None:
            model = q.to_model()
        # page or marker (the last row in the previous page)
        query_result = transaction_service.get_transactions(model, limit,
                                                            marker)
        logger.debug("Getting audit records...end")
        return query_result

    """

    """

    @wsexpose(None, body=Transaction, status_code=201,
              rest_content_types='json')
    def post(self, transaction_input):
        """add a new transaction.

        :param transaction_input: the new transaction values

        Example of usage:
        http://127.0.0.1:8777/v1/audit/transaction
        Headers: Content-Type=application/json
        Body:{
            "timestamp":111,
            "user_id":"user1",
            "application_id":"application_id1",
            "tracking_id":"tracking_id1",
            "external_id":"external_id1",
            "transaction_id":"transaction_id1",
            "transaction_type":"transaction_type1",
            "event_details":"event_details1",
            "status":"status1",
            "resource_id":"resource_id1",
            "service_name":"service_name1"
           }
        """
        logger.debug("Posting new audit record...start")
        logger.info("Posting new audit record: [{}]".format(
            transaction_input))
        model = transaction_input.to_model()
        transaction_service.add_transaction(model)
        logger.debug("Auditing record...end")
