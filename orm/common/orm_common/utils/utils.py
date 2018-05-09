import logging
import pprint
import time

import requests

from orm.common.client.audit.audit_client.api import audit
from pecan import conf

# from cms_rest.logger import get_logger
#

conf = None
logger = logging.getLogger(__name__)


class ResponseError(Exception):
    pass


class ConnectionError(Exception):
    pass


def set_utils_conf(_conf):
    global conf
    conf = _conf


def _check_conf_initialization():
    if not conf:
        raise AssertionError(
            'Configurations wasnt initiated, please run set_utils_conf and '
            'pass pecan coniguration')


def create_or_validate_uuid(uuid, uuid_type):
    """ function to:
            1) request new uuid from uuid_generator rest service
            2) validate a uuid if one is being set
        returns uuid string
    """
    _check_conf_initialization()
    url = conf.api.uuid_server.base + conf.api.uuid_server.uuids

    if not uuid:
        logger.debug('Requesting new UUID from URL: {}'.format(url))
    else:
        logger.debug('Creating UUID: {}, using URL: {}'.format(uuid, url))

    try:
        resp = requests.post(url, data={'uuid': uuid, 'uuid_type': uuid_type},
                             verify=conf.verify)
    except requests.exceptions.ConnectionError as exp:
        nagios = 'CON{}UUIDGEN001'.format(conf.server.name.upper())
        logger.critical(
            'CRITICAL|{}|Failed in make_uuid: connection error: {}'.format(
                nagios, str(exp)))
        exp.message = 'connection error: Failed to get uuid: unable to connect to server'
        raise
    except Exception as e:
        logger.info('Failed in make_uuid:' + str(e))
        return None

    if resp.status_code == 400:
        logger.debug('Duplicate key for uuid: {}'.format(uuid))
        raise TypeError('Duplicate key for uuid: ' + str(uuid))

    resp = resp.json()
    return resp['uuid']


def make_transid():
    """ function to request new uuid of transaction type from uuid_generator
    rest service
        returns uuid string
    """
    _check_conf_initialization()
    url = conf.api.uuid_server.base + conf.api.uuid_server.uuids

    try:
        logger.debug('Requesting transaction ID from: {}'.format(url))
        resp = requests.post(url, data={'uuid_type': 'transaction'}, verify=conf.verify)
    except requests.exceptions.ConnectionError as exp:
        nagios = 'CON{}UUIDGEN001'.format(conf.server.name.upper())
        logger.critical('CRITICAL|{}|Failed in make_transid: connection error: {}'.format(nagios, str(exp)))
        exp.message = 'connection error: Failed to get uuid: unable to connect to server'
        raise
    except Exception as e:
        logger.info('Failed in make_transid:' + str(e))
        return None

    resp = resp.json()
    if 'uuid' in resp:
        return resp['uuid']
    else:
        return None


audit_setup = False


def _get_event_details(cmd):
    event = 'unknown'
    if 'customer' in cmd:
        event = 'CMS'
    elif 'image' in cmd:
        event = 'IMS'
    elif 'flavor' in cmd:
        event = 'FMS'
    return event


def audit_trail(cmd, transaction_id, headers, resource_id, message=None,
                event_details=''):
    """ function to send item to audit trail rest api
        returns 200 for ok and None for error
    :param cmd:
    :param transaction_id:
    :param headers:
    :param resource_id:
    :param message:
    :return:
    """
    _check_conf_initialization()
    global audit_setup, audit_server_url
    if not audit_setup:
        audit_server_url = '%s%s' % (
            conf.api.audit_server.base, conf.api.audit_server.trans)
        num_of_send_retries = 3
        time_wait_between_retries = 1
        logger.debug('Initializing Audit, using URL: {}'.format(
            audit_server_url))
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries, conf.server.name.upper())
        audit_setup = True

    try:
        timestamp = long(round(time.time() * 1000))
        application_id = headers[
            'X-RANGER-Client'] if 'X-RANGER-Client' in headers else \
            'NA'
        tracking_id = headers[
            'X-RANGER-Tracking-Id'] if 'X-RANGER-Tracking-Id' in headers \
            else transaction_id
        # transaction_id is function argument
        transaction_type = cmd
        # resource_id is function argument
        service_name = conf.server.name.upper()
        user_id = headers[
            'X-RANGER-Requester'] if 'X-RANGER-Requester' in headers else \
            ''
        external_id = 'NA'
        logger.debug('Sending to audit: timestamp: {}, application_id: {}, '
                     ' tracking_id: {},'
                     ' transaction_type: {}'.format(timestamp, application_id,
                                                    tracking_id,
                                                    transaction_type))
        audit.audit(timestamp, application_id, tracking_id, transaction_id,
                    transaction_type, resource_id, service_name, user_id,
                    external_id, event_details)
    except Exception as e:
        logger.exception('Failed in audit service. ' + str(e))
        return None

    return 200


def report_config(conf, dump_to_log=False, my_logger=None):
    """ return the configuration (which is set by config.py) as a string
    :param conf:
    :param dump_to_log:
    :param my_logger:
    :return:
    """

    ret = pprint.pformat(conf.to_dict(), indent=4)
    effective_logger = my_logger if my_logger else logger
    if dump_to_log:
        effective_logger.info('Current Configuration:\n' + ret)

    return ret


def get_resource_status(resource_id):
    """ Get a resource status from RDS.
    :param resource_id:
    :return:
    """

    url = "{}{}{}".format(conf.api.rds_server.base,
                          conf.api.rds_server.status, resource_id)
    logger.debug('Getting status from: {}'.format(url))
    try:
        result = requests.get(url, verify=conf.verify)
    except Exception as exception:
        logger.debug('Failed to get status: {}'.format(str(exception)))
        return None

    if result.status_code != 200:
        logger.debug('Got invalid response from RDS: code {}'.format(
            result.status_code))
        return None
    else:
        logger.debug('Got response from RDS: {}'.format(result.json()))
        return result.json()


def get_time_human():
    """this function return the timestamp for output JSON
    :return: timestamp in wanted format
    """
    return time.strftime("%a, %b %d %Y, %X (%Z)", time.gmtime())
