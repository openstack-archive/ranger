import json
import logging
from pecan import conf
import requests

from orm.services.resource_distributor.rds.services.base import ErrorMessage
from orm.services.resource_distributor.rds.utils import authentication as AuthService


logger = logging.getLogger(__name__)


headers = {'content-type': 'application/json'}


def _set_headers(region):
    try:
        token_id = AuthService.get_token(region)
        if token_id:
            headers['X-Auth-Token'] = token_id
            headers['X-Auth-Region'] = region
    except Exception:
        logger.error("no token")
    headers['X-AIC-ORM-Requester'] = 'rds_resource_service_proxy'


def invoke_resources_region_delete(resource_type, region, resource_id):
    logger.debug(
        "REGION STATUS PROXY - send delete status to {} service for region {}".format(resource_type, region))

    _set_headers(region)

    try:
        if resource_type == "customer":
            logger.debug("sending the data to {} server delete method ".format(resource_type))
            response = requests.delete(
                conf.cms.base_url + (conf.cms.delete_region).format(resource_id, region),
                headers=headers, verify=conf.verify)
        elif resource_type == "flavor":
            logger.debug("sending the data to {} server delete method ".format(resource_type))
            response = requests.delete(
                conf.fms.base_url + (conf.fms.delete_region).format(resource_id, region),
                headers=headers, verify=conf.verify)
        elif resource_type == "image":
            logger.debug("sending the data to {} server delete method ".format(resource_type))
            response = requests.delete(
                conf.ims.base_url + (conf.ims.delete_region).format(resource_id, region),
                headers=headers, verify=conf.verify)
        else:
            response = None

        logger.debug("got response {} from send delete status to {} service.".
                     format(response, resource_type))
    except requests.ConnectionError as exp:
        logger.error(exp)
        logger.exception(exp)
        raise ErrorMessage("fail to connect to server {}".format(exp.message))

    if response.status_code != 200:
        raise ErrorMessage(
            "Got error from rds server, code: {0} message: {1}".format(
                response.status_code, response.content))
    return


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

    _set_headers(region)
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
            raise ErrorMessage("fail to connect to server {}".format(exp.message))

    if response.status_code != 200:
        raise ErrorMessage(
            "Got error from rds server, code: {0} message: {1}".format(
                response.status_code, response.content))
    return
