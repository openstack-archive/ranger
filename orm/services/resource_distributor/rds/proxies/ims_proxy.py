import json
import logging
import requests

from orm.services.resource_distributor.rds.services.base import ErrorMesage
from orm.services.resource_distributor.rds.utils import authentication as AuthService

from pecan import conf

logger = logging.getLogger(__name__)


headers = {'content-type': 'application/json'}


def _set_headers():
    try:
        region, token_id = AuthService.get_token()
        if token_id:
            headers['X-Auth-Token'] = token_id
            headers['X-Auth-Region'] = region
    except Exception:
        logger.error("no token")


def send_image_metadata(meta_data, region, resource_id, action='post'):
    logger.debug(
        "IMS PROXY - send metadata to ims {} for region {}".format(meta_data,
                                                                   region))
    data_to_send = {
        "metadata": {
            "checksum": meta_data['checksum'],
            "virtual_size": meta_data['virtual_size'],
            "size": meta_data['size']
        }
    }

    _set_headers()
    data_to_send_as_json = json.dumps(data_to_send)
    logger.debug("sending the data to ims server post method ")
    logger.debug("ims server {0} path = {1}".format(conf.ims.base_url,
                                                    conf.ims.metadata_path).format(
        resource_id, region))

    if action == 'post':
        try:
            response = requests.post(
                conf.ims.base_url + (conf.ims.metadata_path).format(resource_id, region),
                data=data_to_send_as_json, headers=headers, verify=conf.verify)
            logger.debug("got response from ims {}".format(response))
        except requests.ConnectionError as exp:
            logger.error(exp)
            logger.exception(exp)
            raise ErrorMesage("fail to connect to server {}".format(exp.message))

    if response.status_code != 200:
        raise ErrorMesage(
            "Got error from orm.services.resource_distributor.rds server, code: {0} message: {1}".format(
                response.status_code, response.content))
    return
