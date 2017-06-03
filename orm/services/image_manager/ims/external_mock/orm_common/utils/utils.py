import requests
import pprint
import logging
from pecan import conf
from audit_client.api import audit
import time

from orm_common.logger import get_logger

logger = get_logger(__name__)

conf = None


def set_utils_conf(_conf):
    global conf
    conf = _conf


def _check_conf_initialization():
    if not conf:
        raise AssertionError(
            'Configurations wasnt initiated, please run set_utils_conf and '
            'pass pecan coniguration')


def make_uuid():
    """ function to request new uuid from uuid_generator rest service
        returns uuid string
    """
    _check_conf_initialization()
    url = conf.api.uuid_server.base + conf.api.uuid_server.uuids

    try:
        resp = requests.post(url)
    except Exception as e:
        logger.info('Failed in make_uuid:' + str(e))
        raise Exception('Failed in make_uuid:' + str(e))

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
        resp = requests.post(url, data={'uuid_type': 'transaction'})
    except Exception as e:
        logger.info('Failed in make_transid:' + str(e))
        raise Exception('Failed in make_transid:' + str(e))

    resp = resp.json()
    return resp['uuid']


audit_setup = False


def audit_trail(cmd, transaction_id, headers, resource_id, message):
    """ function to send item to audit trail rest api
        returns 200 for ok and None for error
    """

    _check_conf_initialization()
    global audit_setup, audit_server_url
    if not audit_setup:
        audit_server_url = '%s%s' % (conf.api.audit_server.base,
                                     conf.api.audit_server.trans)
        num_of_send_retries = 3
        time_wait_between_retries = 1
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries)
        audit_setup = True

    try:
        timestamp = long(round(time.time() * 1000))
        application_id = headers['X-RANGER-Client']
        tracking_id = headers[
            'X-RANGER-Tracking-Id'] if 'X-RANGER-Tracking-Id' in headers \
            else transaction_id
        # transaction_id is function argument
        transaction_type = cmd
        # resource_id is function argument
        service_name = conf.server.name
        user_id = headers[
            'X-RANGER-Requester'] if 'X-RANGER-Requester' in headers else 'NA'
        external_id = 'NA'
        event_details = 'CMS'
        status = message
        audit.audit(timestamp, application_id, tracking_id, transaction_id,
                    transaction_type,
                    resource_id, service_name, user_id, external_id,
                    event_details, status)
    except Exception as e:
        logger.log_exception('Failed in audit service', e)
        return None

    return 200


def report_config(conf, dump_to_log=False, my_logger=None):
    """ return the configuration (which is set by config.py) as a string
    """

    ret = pprint.pformat(conf.to_dict(), indent=4)
    effective_logger = my_logger if my_logger else logger
    if dump_to_log:
        effective_logger.info('Current Configuration:\n' + ret)

    return ret
