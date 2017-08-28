import time

import requests

from orm.common.orm_common.logger import get_logger
from pecan import conf

logger = get_logger(__name__)

conf = None


def set_utils_conf(_conf):
    global conf
    conf = _conf


def _check_conf_initialization():
    if not conf:
        raise AssertionError(
            'Configuration wasnt initiated, please run set_utils_conf and '
            'pass pecan configuration')


def is_region_exist(region_name):
    """ function to check whether region exists
        returns 200 for ok and None for error
    """
    region = get_rms_region(region_name)
    if region is None:
        return False

    return True


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

    return group["Regions"]


def get_rms_region(region_name):
    """ function to call rms api for region info
        returns 200 for ok and None for error
    """
    _check_conf_initialization()
    try:
        headers = {
            'content-type': 'application/json',
        }
        rms_server_url = '%s%s/%s' % (
            conf.api.rms_server.base, conf.api.rms_server.regions, region_name)
        resp = requests.get(rms_server_url, headers=headers).json()
        return resp
    except Exception as e:
        logger.log_exception('Failed in get_rms_region', e)
        return None

    return 200


prev_group_name = None


def get_rms_region_group(group_name):
    """ function to call rms api for group info
        returns 200 for ok and None for error
    """
    global prev_group_name, prev_timestamp, prev_resp

    _check_conf_initialization()
    try:
        timestamp = time.time()
        if group_name == prev_group_name and timestamp - prev_timestamp <= \
                conf.api.rms_server.cache_seconds:
            return prev_resp

        headers = {
            'content-type': 'application/json',
        }
        rms_server_url = '%s%s/%s' % (
            conf.api.rms_server.base, conf.api.rms_server.groups, group_name)
        resp = requests.get(rms_server_url, headers=headers).json()
        prev_resp = resp
        prev_group_name = group_name
        prev_timestamp = timestamp
        return resp
    except Exception as e:
        logger.log_exception('Failed in get_rms_region_group', e)
        return None

    return 200
