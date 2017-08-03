import logging
import time

import requests

from pecan import conf

# from orm_common.logger import get_logger

# logger = get_logger(__name__)
logger = logging.getLogger(__name__)

conf = None


def set_utils_conf(_conf):
    global conf
    conf = _conf


def _check_conf_initialization():
    if not conf:
        raise AssertionError('Configurations wasnt initiated, please run set_utils_conf and pass pecan configuration')


def is_region_group_exist(group_name):
    """ function to check whether region group exists
        returns 200 for ok and None for error
    """
    group = get_rms_region_group(group_name)
    if group is None:
        return False

    return True


def get_regions_of_group(group_name):
    """ function to get regions associated with group
        returns 200 for ok and None for error
    """
    group = get_rms_region_group(group_name)
    if group is None:
        return None
    if "regions" not in group:
        return None
    return group["regions"]


prev_group_name = None


def get_rms_region_group(group_name):
    """ function to call rms api for group info
        returns 200 for ok and None for error
    """
    global prev_group_name, prev_timestamp, prev_resp

    _check_conf_initialization()
    try:
        timestamp = time.time()
        if group_name == prev_group_name and timestamp - prev_timestamp <= conf.api.rms_server.cache_seconds:
            return prev_resp

        headers = {
            'content-type': 'application/json',
        }
        # GET https://{serverRoot}/v1/orm/groups/{groupId}/
        rms_server_url = '%s%s/%s' % (conf.api.rms_server.base, conf.api.rms_server.groups, group_name)
        logger.info("RMS Server URL:" + rms_server_url)
        resp = requests.get(rms_server_url, headers=headers, verify=conf.verify)
        resp = resp.json()
        logger.info("Response from RMS Server" + str(resp))
        prev_resp = resp
        prev_group_name = group_name
        prev_timestamp = timestamp
        return resp
    except requests.exceptions.ConnectionError as exp:
        nagois = 'CON{}RMS001'.format(conf.server.name.upper())
        logger.error(
            'CRITICAL|{}| Failed in getting data from rms: connection error'.format(
                nagois) + str(exp))
        exp.message = 'connection error: Failed to get get data from rms: unable to connect to server'
        raise
    except Exception as e:
        logger.exception(" Exception: " + str(e))
        # logger.log_exception('Failed in get_rms_region_group', e)
        raise
