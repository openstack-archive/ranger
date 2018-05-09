"""module"""
import logging
import re
import requests

from orm.services.resource_distributor.rds.proxies import ims_proxy
from orm.services.resource_distributor.rds.services.base import ErrorMessage

from pecan import conf

logger = logging.getLogger(__name__)


def post_data_to_image(data):
    if data['resource_type'] == "image" and data['resource_operation'] != 'delete' and 'resource_extra_metadata' in data:
        logger.debug("send metadata {} to ims :- {} for region {}".format(
            data['resource_extra_metadata'], data['resource_id'], data['region']))

        ims_proxy.send_image_metadata(
            meta_data=data['resource_extra_metadata'],
            resource_id=data['resource_id'], region=data['region'])

    return


def invoke_delete_region(data):
    if data['resource_operation'] == 'delete' and (data['status'] == 'Success' or data['error_code'] == 'ORD_012'):
        ims_proxy.invoke_resources_region_delete(
            resource_type=data['resource_type'],
            resource_id=data['resource_id'], region=data['region'])

    return


def _get_all_rms_regions():
    # rms url
    discover_url = '%s:%d' % (conf.ordupdate.discovery_url,
                              conf.ordupdate.discovery_port,)
    # get all regions
    response = requests.get('%s/v2/orm/regions' % (discover_url),
                            verify=conf.verify)

    if response.status_code != 200:
        # fail to get regions
        error = "got bad response from rms {}".format(response)
        logger.error(error)
        raise ErrorMessage(message="got bad response from rms ")

    return response.json()


def _validate_version(region, supported_resource_version):
    version = region['version'] and re.findall(r'[\d+\.\d]+', region['version'])
    supported_resource_min_version = float(supported_resource_version[0]) if supported_resource_version else 0
    if version:
        version = version[0].strip().split('.')
        version = version[0] + '.' + ''.join(version[1:])
    if not version or float(version) < supported_resource_min_version:
        return None
    return float(version)


def add_rms_status_to_regions(resource_regions, resource_type):
    rms_regions = {}
    all_regions = _get_all_rms_regions()
    supported_versions = conf.region_resource_id_status.allowed_aic_resource_version

    supported_resource_version = [value for key, value in supported_versions if key == resource_type]

    # iterate through rms regions and gett regions status and version
    for region in all_regions['regions']:
        rms_regions[region['name']] = {'status': region['status'],
                                       'version': region['aicVersion']}

    # iterate through resource regions and add to them rms status
    for region in resource_regions:
        if region['name'] in rms_regions:
            # check if version valid
            region['aicVersion'] = _validate_version(rms_regions[region['name']],
                                                     supported_resource_version)
            if not region['aicVersion']:
                raise ErrorMessage(
                    message="aic version for region {} must be >={} ".format(
                        region['name'], supported_resource_version[0] if supported_resource_version else '0'))

            region['rms_status'] = rms_regions[region['name']]['status']
            continue
        # if region not found in rms
        region['rms_status'] = "region_not_found_in_rms"
    return resource_regions
