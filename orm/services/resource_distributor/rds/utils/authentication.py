import json
import logging
import requests

from orm.common.client.keystone.keystone_utils import tokens
from orm.services.resource_distributor.rds.proxies import rms_proxy as RmsService

from pecan import conf

enabled = False
mech_id = ""
mech_password = False
rms_url = ""
tenant_name = ""
keystone_version = ""
user_domain_name = "default"
project_domain_name = "default"


headers = {'content-type': 'application/json'}


logger = logging.getLogger(__name__)


def _is_authorization_enabled():
    return conf.authentication.enabled


def _get_token_conf():
    conf = tokens.TokenConf(mech_id, mech_password, rms_url, tenant_name,
                            keystone_version, user_domain_name, project_domain_name)
    return conf


def get_keystone_ep_region_name(region):
    # get  end point of a region
    region_data = RmsService.get_rms_region(region)
    if not region_data:
        logger.error("fail to get region from rms")
        return None
    logger.debug("got rms region {} for region name {} ".format(
        region, region_data))
    keystone_ep = None
    for endpoint in region_data['endpoints']:
        if endpoint['type'] == 'identity':
            keystone_ep = endpoint['publicURL']
            break

    logger.debug("Got keystone_ep {} for region name {}".format(keystone_ep,
                                                                region))
    return keystone_ep


def get_token(region):
    V3_TOKEN_GET_SUCCESS = 201

    logger.debug("create token")
    if not _is_authorization_enabled():
        return

    keystone_ep = get_keystone_ep_region_name(region)
    if not region or not keystone_ep:
        log_message = "fail to create token reason -- fail to get region-- " \
                      "region:{} keystone {}".format(region, keystone_ep)
        log_message = log_message.replace('\n', '_').replace('\r', '_')
        logger.error(log_message)
        return

    url = keystone_ep + '/{}/auth/tokens'.format(conf.token_version)

    data = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "name": conf.authentication.mech_id,
                        "domain": {
                            "name": user_domain_name
                        },
                        "password": conf.authentication.mech_pass
                    }
                }
            },
            "scope": {
                "project": {
                    "domain": {
                        "name": project_domain_name
                    },
                    "name": conf.authentication.tenant_name
                }
            }
        }
    }

    try:
        logger.debug("get token url- {}".format(url))
        resp = requests.post(url, data=json.dumps(data), headers=headers)

        if resp.status_code != V3_TOKEN_GET_SUCCESS:
            logger.error("fail to get token from url")
        logger.debug("got token for region {}".format(region))
        return resp.headers['x-subject-token']

    except Exception as exp:
        logger.error(exp)
        logger.exception(exp)
