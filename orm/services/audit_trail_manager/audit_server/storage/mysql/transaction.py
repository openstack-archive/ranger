"""mysql transaction module."""

import logging

from audit_server.model.transaction import Model
from audit_server.storage import transaction
from sqlalchemy import BigInteger, Column, Integer, Text, asc, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
logger = logging.getLogger(__name__)


class Record(Base):
    """record base class."""

    __tablename__ = 'transactions'

    id = Column(Integer, autoincrement=True, primary_key=True)
    timestamp = Column(BigInteger)
    user_id = Column(Text)
    application_id = Column(Text)
    tracking_id = Column(Text)
    external_id = Column(Text)
    transaction_id = Column(Text)
    transaction_type = Column(Text)
    event_details = Column(Text)
    resource_id = Column(Text)
    service_name = Column(Text)


class Connection(transaction.Base):
    """Implements mysql DB."""

    def __init__(self, url, echo_statements):
        """init method."""
        self._engine = create_engine(url, echo=echo_statements)
        self._session_maker = sessionmaker(bind=self._engine)
        pass

    def add_record(self, transaction_record):
        """add a new transaction record.

        :param transaction_record: the new transaction record.
        """
        logger.debug(
            "Auditing record: [{}] ...start".format(transaction_record))
        try:
            session = self._session_maker()
            session.add(Record(timestamp=transaction_record.timestamp,
                               user_id=transaction_record.user_id,
                               application_id=transaction_record.
                               application_id,
                               tracking_id=transaction_record.tracking_id,
                               external_id=transaction_record.external_id,
                               transaction_id=transaction_record.
                               transaction_id,
                               transaction_type=transaction_record.
                               transaction_type,
                               event_details=transaction_record.event_details,
                               resource_id=transaction_record.resource_id,
                               service_name=transaction_record.service_name))
            session.commit()
        # All other exceptions will be raised
        except IntegrityError as e:
            # Except Exception as e:
            session.rollback()
            # Raise the exception only if it's not a duplicate entry exception
            if 'duplicate entry' in e.message.lower():
                logger.warning(
                    "Fail to audit record - Duplicate entry: {}".format(
                        e))
            else:
                logger.warning("Fail to audit record: {}".format(e))
                raise e

        finally:
            session.close()
        logger.debug("Auditing record...end")

    def get_records(self, query, limit=10, marker=None):
        """get all records records that meet the given query.

        :param q: the query to use in order to search for relevant.
        records.
        :param limit: the maximun number of records to return.
        :param marker: a place order for pagination (not implemented yet).
        """
        logger.debug("Getting records using query:[{}]...start".format(query))
        try:
            session = self._session_maker()
            records = session.query(Record)
            if query is not None:
                records = Connection._add_filter(records, query, marker)
            records = records.order_by(asc(Record.timestamp))
            records = records.limit(limit)
            records_result = records.all()
            transactions = []
            for record in records_result:
                timestamp = record.timestamp
                user_id = record.user_id
                application_id = record.application_id
                tracking_id = record.tracking_id
                external_id = record.external_id
                transaction_id = record.transaction_id
                transaction_type = record.transaction_type
                event_details = record.event_details
                resource_id = record.resource_id
                service_name = record.service_name
                model = Model(timestamp, user_id, application_id, tracking_id,
                              external_id, transaction_id, transaction_type,
                              event_details, resource_id, service_name)
                transactions.append(model)
            logger.debug(
                "Getting records using query:[{}] "
                "return the result :[{}]...start".format(
                    query, transactions))
            logger.debug("Getting records using query...end")
            return transactions
        finally:
            session.close()

    @staticmethod
    def _add_filter(records, query, marker):
        """add filter to the select based on the given query.

        :param records: the records created so far.
        :param query: the query to use in order to search for relevant.
        records.
        :param marker: a place order for pagination (not implemented yet).
        """
        logger.debug("add_filter for query: [{}] ...start".format(query))
        if marker is not None:
            records = records.filter(Record.timestamp > marker)
        if query.timestamp_from is not None:
            records = records.filter(Record.timestamp >= query.timestamp_from)
        if query.timestamp_to is not None:
            records = records.filter(Record.timestamp <= query.timestamp_to)
        records = Connection._add_filter_eq(records, Record.user_id,
                                            query.user_id)
        records = Connection._add_filter_eq(records, Record.application_id,
                                            query.application_id)
        records = Connection._add_filter_eq(records, Record.tracking_id,
                                            query.tracking_id)
        records = Connection._add_filter_eq(records, Record.external_id,
                                            query.external_id)
        records = Connection._add_filter_eq(records, Record.transaction_id,
                                            query.transaction_id)
        records = Connection._add_filter_eq(records, Record.transaction_type,
                                            query.transaction_type)
        records = Connection._add_filter_eq(records, Record.event_details,
                                            query.event_details)
        records = Connection._add_filter_eq(records, Record.resource_id,
                                            query.resource_id)
        records = Connection._add_filter_eq(records, Record.service_name,
                                            query.service_name)
        logger.debug("add_filter for query: [{}] ...end".format(query))
        return records

    @staticmethod
    def _add_filter_eq(records, key, value):
        if value is not None:
            records = records.filter(key == value)
        return records
