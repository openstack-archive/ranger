"""python module."""

import json
import logging
import requests

from pecan import conf
from rds.services.base import ErrorMesage


logger = logging.getLogger(__name__)


headers = {'content-type': 'application/json'}


def get_regions():
    logger.debug("get list of regions from rms")
    logger.debug("rms server {0} path = {1}".format(conf.rms.base_url,
                                                    conf.rms.all_regions_path))

    response = requests.get(conf.rms.base_url + conf.rms.all_regions_path,
                            headers=headers, verify=conf.verify)

    if response.status_code != 200:
        log_message = "not able to get regions {}".format(response)
        log_message = log_message.replace('\n', '_').replace('\r', '_')
        logger.error(log_message)
        return

    return response.json()
