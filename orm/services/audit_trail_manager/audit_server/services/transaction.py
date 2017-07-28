"""transaction service module."""

import logging

from audit_server.model.transaction_query_result import \
    Model as QueryResultModel
from audit_server.storage import factory

logger = logging.getLogger(__name__)


def add_transaction(transaction):
    """add a new transaction.

    :param transaction: the new transaction object.
    """
    logger.debug("Auditing record: [{}] ...start".format(transaction))
    conn = factory.get_transaction_connection()
    conn.add_record(transaction)
    logger.debug("Auditing record...end")


def get_transactions(query, limit, marker):
    """get all transactions that meet the given query.

    :param q: the query to use in order to search for relevant.
    transactions.
    :param limit: the maximun number of transactions to return.
    :param marker: a place order for pagination (not implemented yet).
    """
    logger.debug("Getting records for query:{}...start".format(query))
    conn = factory.get_transaction_connection()
    transactions = conn.get_records(query, limit, marker)
    logger.debug("Getting records for query...end")
    return QueryResultModel(transactions)
