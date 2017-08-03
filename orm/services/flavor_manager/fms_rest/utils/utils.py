import time

from fms_rest.logger import get_logger
from orm_common.injector import injector
from pecan import conf

logger = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('requests')
def make_uuid():
    """ function to request new uuid from uuid_generator rest service
        returns uuid string
    """

    requests = di.resolver.unpack(make_uuid)
    url = conf.api.uuid_server.base + conf.api.uuid_server.uuids

    try:
        resp = requests.post(url, verify=conf.verify)
    except requests.exceptions.ConnectionError as exp:
        nagios = 'CON{}UUIDGEN001'.format(conf.server.name.upper())
        logger.critical(
            'CRITICAL|{}|Failed in make_uuid: connection error: {}'.format(
                nagios, str(exp)))
        exp.message = 'connection error: Failed to get uuid: unable to connect to server'
        raise
    except Exception as e:
        logger.info('Failed in make_uuid:' + str(e))
        raise Exception('Failed in make_uuid:' + str(e))

    resp = resp.json()
    return resp['uuid']


@di.dependsOn('requests')
def create_existing_uuid(uuid):
    """ function to request new uuid from uuid_generator rest service
        returns uuid string
    """

    requests = di.resolver.unpack(make_uuid)
    url = conf.api.uuid_server.base + conf.api.uuid_server.uuids

    try:
        logger.debug('Creating UUID: {}, using URL: {}'.format(uuid, url))
        resp = requests.post(url, data={'uuid': uuid}, verify=conf.verify)
    except requests.exceptions.ConnectionError as exp:
        nagios = 'CON{}UUIDGEN001'.format(conf.server.name.upper())
        logger.critical(
            'CRITICAL|{}|Failed in create_existing_uuid: connection error: {}'.format(
                nagios, str(exp)))
        exp.message = 'connection error: Failed to get uuid: unable to connect to server'
        raise
    except Exception as e:
        logger.info('Failed in make_uuid:' + str(e))
        return None

    if resp.status_code == 400:
        raise TypeError('duplicate key for uuid')
    resp = resp.json()
    return resp['uuid']


@di.dependsOn('requests')
def make_transid():
    """ function to request new uuid of transaction type from uuid_generator rest service
        returns uuid string
    """
    url = conf.api.uuid_server.base + conf.api.uuid_server.uuids
    requests = di.resolver.unpack(make_uuid)

    try:
        resp = requests.post(url, data={'uuid_type': 'transaction'},
                             verify=conf.verify)
    except requests.exceptions.ConnectionError as exp:
        nagios = 'CON{}UUIDGEN001'.format(conf.server.name.upper())
        logger.critical(
            'CRITICAL|{}|Failed in make_transid: connection error: {}'.format(
                nagios, str(exp)))
        exp.message = 'connection error: Failed to get uuid: unable to connect to server'
        raise
    except Exception as e:
        logger.info('Failed in make_transid:' + str(e))
        raise Exception('Failed in make_transid:' + str(e))

    resp = resp.json()
    if 'uuid' in resp:
        return resp['uuid']
    else:
        return None

audit_setup = False


@di.dependsOn('audit_client')
def audit_trail(cmd, transaction_id, headers, resource_id, event_details=''):
    """ function to send item to audit trail rest api
        returns 200 for ok and None for error
    """
    audit = di.resolver.unpack(audit_trail)

    global audit_setup, audit_server_url
    if not audit_setup:
        audit_server_url = '%s%s' % (conf.api.audit_server.base, conf.api.audit_server.trans)
        num_of_send_retries = 3
        time_wait_between_retries = 1
        audit.init(audit_server_url, num_of_send_retries,
                   time_wait_between_retries, conf.server.name.upper())
        audit_setup = True

    try:
        timestamp = long(round(time.time() * 1000))
        application_id = headers['X-RANGER-Client'] if 'X-RANGER-Client' in headers else 'NA'
        tracking_id = headers['X-RANGER-Tracking-Id'] if 'X-RANGER-Tracking-Id' in headers else transaction_id
        # transaction_id is function argument
        transaction_type = cmd
        # resource_id is function argument
        service_name = conf.server.name.upper()
        user_id = headers['X-RANGER-Requester'] if 'X-RANGER-Requester' in headers else ''
        external_id = 'NA'
        audit.audit(timestamp, application_id, tracking_id, transaction_id, transaction_type,
                    resource_id, service_name, user_id, external_id, event_details)
    except Exception as e:
        logger.log_exception('Failed in audit_trail(cmd=%s, id=%s) url: %s' % (cmd, id, audit_server_url), e)
        raise e

    return 200
