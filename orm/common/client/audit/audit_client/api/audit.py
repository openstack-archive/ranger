"""audit module."""

import json
import logging
import threading
import time
import urllib2

from audit_client.api.exceptions.audit_exception import AuditException
from audit_client.api.model.get_audits_result import AuditsResult
from audit_client.api.model.transaction import Transaction

logger = logging.getLogger(__name__)

config = {
    'AUDIT_SERVER_URL': None,
    'NUM_OF_SEND_RETRIES': None,
    'TIME_WAIT_BETWEEN_RETRIES': None,
    'SERVICE_NAME': None}


def init(audit_server_url, num_of_send_retries, time_wait_between_retries,
         service_name=''):
    """Initialize the audit client.

    :param audit_server_url: audit server url
    :param num_of_send_retries: number of times to try and send the record
    in case of failures.
    :param time_wait_between_retries: how much time to wait (in seconds)
    between each retry.
    """
    if not audit_server_url \
            or not num_of_send_retries \
            or not time_wait_between_retries:
        error_msg = "Error: Fail to initialize audit using following inputs " \
                    "AUDIT_SERVER_URL={}, NUM_OF_SEND_RETRIES={}, " \
                    "TIME_WAIT_BETWEEN_RETRIES={}. " \
                    "One of them is possibly None" \
            .format(audit_server_url, num_of_send_retries,
                    time_wait_between_retries)
        logger.error(error_msg)
        raise AuditException(error_msg)

    config['AUDIT_SERVER_URL'] = audit_server_url
    config['NUM_OF_SEND_RETRIES'] = num_of_send_retries
    config['TIME_WAIT_BETWEEN_RETRIES'] = time_wait_between_retries
    config['SERVICE_NAME'] = service_name


def _validate():
    """# Validate proper initialization of the audit client."""
    # if not AUDIT_SERVER_URL or not NUM_OF_SEND_RETRIES
    # or not TIME_WAIT_BETWEEN_RETRIES:
    if not config['AUDIT_SERVER_URL'] \
            or not config['NUM_OF_SEND_RETRIES'] \
            or not config['TIME_WAIT_BETWEEN_RETRIES']:
        raise AuditException(
            "Error: Audit was not initialize correctly. You must first "
            "run audit.init(audit_server_url, num_of_send_retries, "
            "time_wait_between_retries)")


def audit(timestamp, application_id, tracking_id, transaction_id,
          transaction_type, resource_id, service_name, user_id=None,
          external_id=None, event_details=None):
    """The method is used to audit transactions.

    :param timestamp:
    :param application_id:
    :param tracking_id:
    :param transaction_id:
    :param transaction_type:
    :param resource_id:
    :param service_name:
    :param user_id:
    :param external_id:
    :param event_details:
    :return:
    """
    thread = threading.Thread(target=_audit_thread, args=(
        timestamp, application_id, tracking_id, transaction_id,
        transaction_type,
        resource_id, service_name, user_id, external_id, event_details))
    thread.start()


def get_audits(timestamp_from=None, timestamp_to=None, application_id=None,
               tracking_id=None, transaction_id=None, transaction_type=None,
               resource_id=None, service_name=None, user_id=None,
               external_id=None, event_details=None, limit=None):
    """The method is used to audit transactions.

    :param timestamp_from:
    :param timestamp_to:
    :param application_id:
    :param tracking_id:
    :param transaction_id:
    :param transaction_type:
    :param resource_id:
    :param service_name:
    :param user_id:
    :param external_id:
    :param event_details:
    """
    query = ""
    query = _build_query(query, "q.timestamp_from", timestamp_from)
    query = _build_query(query, "q.timestamp_to", timestamp_to)
    query = _build_query(query, "q.application_id", application_id)
    query = _build_query(query, "q.tracking_id", tracking_id)
    query = _build_query(query, "q.transaction_id", transaction_id)
    query = _build_query(query, "q.transaction_type", transaction_type)
    query = _build_query(query, "q.resource_id", resource_id)
    query = _build_query(query, "q.service_name", service_name)
    query = _build_query(query, "q.user_id", user_id)
    query = _build_query(query, "q.external_id", external_id)
    query = _build_query(query, "q.event_details", event_details)
    query = _build_query(query, "limit", limit)
    payload = _get_data(query)
    data = json.load(payload)
    transactions = []
    for transaction in data['transactions']:
        timestamp = transaction['timestamp']
        user_id = transaction['user_id']
        application_id = transaction['application_id']
        tracking_id = transaction['tracking_id']
        external_id = transaction['external_id']
        transaction_id = transaction['transaction_id']
        resource_id = transaction['resource_id']
        service_name = transaction['service_name']
        transaction_type = transaction['transaction_type']
        event_details = transaction['event_details']
        transactions.append(
            Transaction(timestamp, user_id, application_id, tracking_id,
                        external_id, transaction_id, transaction_type,
                        event_details, resource_id, service_name))
    return AuditsResult(transactions)


def _build_query(query, arg_name, arg_value):
    if arg_value is not None:
        query = query + "%s=%s&" % (arg_name, arg_value)
    return query


# A thread method for sending data to the audit server
# This method is asynchronic in order to prevent blocking
def _audit_thread(timestamp, application_id, tracking_id, transaction_id,
                  transaction_type, resource_id, service_name, user_id,
                  external_id, event_details):
    # Prepare the data for the audit server
    data = {
        "timestamp": timestamp,
        "application_id": application_id,
        "tracking_id": tracking_id,
        "transaction_id": transaction_id,
        "transaction_type": transaction_type,
        "resource_id": resource_id,
        "service_name": service_name,
        "user_id": user_id,
        "external_id": external_id,
        "event_details": event_details,
        "resource_id": resource_id,
        "service_name": service_name
    }
    _post_data(data)


def _post_data(data):
    # Validate that the configuration was initialized
    _validate()
    # Send the data
    req = urllib2.Request(config['AUDIT_SERVER_URL'])
    req.add_header('Content-Type', 'application/json')
    # Retry to send the data to the audit server
    success = False
    for retry_number in range(config['NUM_OF_SEND_RETRIES']):
        try:
            urllib2.urlopen(req, json.dumps(data))
            success = True
            break
        except Exception as error:
            time.sleep(config['TIME_WAIT_BETWEEN_RETRIES'])

    if not success:
        error_msg = "ERROR|CON{}AUDIT001|Fail to send data to [{}]. Tried " \
                    "a couple of times with no success. Last attempt " \
                    "error: [{}]".format(config['SERVICE_NAME'],
                                         config['AUDIT_SERVER_URL'],
                                         error.message)
        logger.error(error_msg)
        raise AuditException(error_msg)


def _get_data(query):
    # Validate that the configuration was initialized
    _validate()
    # Send the data
    audit_server_url_with_query = "{}?{}".format(config['AUDIT_SERVER_URL'],
                                                 query)
    req = urllib2.Request(audit_server_url_with_query)
    # Retry to get the data from the audit server
    success = False
    response = None
    for retry_number in range(config['NUM_OF_SEND_RETRIES']):
        try:
            response = urllib2.urlopen(req)
            success = True
            break
        except Exception as error:
            time.sleep(config['TIME_WAIT_BETWEEN_RETRIES'])

    if not success:
        error_msg = "Fail to get data from [{}]. Tried a couple of times " \
                    "with no success. Last attempt error: [{}]".\
            format(audit_server_url_with_query, error.message)
        logger.error(error_msg)
        raise AuditException(error_msg)
    else:
        return response
