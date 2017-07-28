"""module"""
import logging
import requests
from pecan import conf
from rds.services.base import ErrorMesage
from rds.proxies import ims_proxy

logger = logging.getLogger(__name__)


def post_data_to_image(data):
    if data['resource_type'] == "image" and 'resource_extra_metadata' in data:
        logger.debug("send metadata {} to ims :- {} for region {}".format(
            data['resource_extra_metadata'], data['resource_id'], data['region']))

        ims_proxy.send_image_metadata(
            meta_data=data['resource_extra_metadata'],
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
        raise ErrorMesage(message="got bad response from rms ")

    return response.json()


def _validate_version(region, resource_type):
    version = None
    if 'ranger_agent' in region['version'].lower():
        version = region['version'].lower().split('ranger_agent')[1].strip().split('.')
        version = version[0] + '.' + ''.join(version[1:])
    if not version or float(version) < 3:
        return False
    return True


def add_rms_status_to_regions(resource_regions, resource_type):
    rms_regions = {}
    all_regions = _get_all_rms_regions()

    # iterate through rms regions and gett regions status and version
    for region in all_regions['regions']:
        rms_regions[region['name']] = {'status': region['status'],
                                       'version': region['rangerAgentVersion']}

    # iterate through resource regions and add to them rms status
    for region in resource_regions:
        if region['name'] in rms_regions:
            # check if version valid
            if not _validate_version(rms_regions[region['name']],
                                     resource_type):
                raise ErrorMesage(
                    message="ranger_agent version for region {} must be >=1.0 ".format(
                        region['name']))

            region['rms_status'] = rms_regions[region['name']]['status']
            continue
        # if region not found in rms
        region['rms_status'] = "region_not_found_in_rms"
    return resource_regions
