import logging
import pprint
import time

import requests
import uuid

from orm.common.client.audit.audit_client.api import audit
from orm.common.orm_common.db.db_manager import DBManager

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


def create_or_validate_uuid(id, uuid_type):
    """ function to:
            1) request new uuid
            2) validate a uuid if one is being set
        returns uuid string
    """
    if not id or id == 'Unset':
        id = uuid.uuid4().hex

    try:
        db_manager = DBManager()
        db_manager.create_uuid(id, uuid_type)
        return id
    except Exception as e:
        # ignore case of uuid already exist, this can append when creating customer with specific uuid,
        # we just need to save it in the database that we will not give this value in the future requests
        # but we don't need to throw exception if already exist, this is not our responsible
        # if it is duplicate uuid it will fail in the service which uses this uuid (cms, fms)
        if e.inner_exception.orig[0] == 1062:
            LOG.info("Duplicate UUID=" + uuid)
        else:
            LOG.error(str(messageToReturn) + "Exception: " + str(e))
            raise ResponseError('Database Error')
    return id


def make_transid():
    return create_or_validate_uuid(None, 'transaction')


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
