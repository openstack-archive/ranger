"""python module."""

import logging
from pecan import conf
import requests

logger = logging.getLogger(__name__)


def get_rms_region(region_name):
    """ function to call rms api for region info
        returns 200 for ok and None for error
    """
    try:
        headers = {
            'content-type': 'application/json',
        }
        rms_server_url = '%s%s/%s' % (
            conf.rms.base_url, conf.rms.all_regions_path, region_name)
        resp = requests.get(rms_server_url, headers=headers,
                            verify=conf.verify).json()
        return resp
    except Exception as e:
        logger.log_exception('Failed in get_rms_region', e)
        return None
