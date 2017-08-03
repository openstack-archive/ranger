import json
import logging

import requests

from keystone_utils import tokens
from pecan import conf
from rds.proxies import rms_proxy as RmsService

enabled = False
mech_id = ""
mech_password = False
rms_url = ""
tenant_name = ""


headers = {'content-type': 'application/json'}


logger = logging.getLogger(__name__)


def _is_authorization_enabled():
    return conf.authentication.enabled


def _get_token_conf():
    conf = tokens.TokenConf(mech_id, mech_password, rms_url, tenant_name)
    return conf


def get_keystone_ep_region_name():
    # get any region that hase keystone end point
    logger.debug("get list of regions from rms")
    regions = RmsService.get_regions()
    if not regions:
        logger.error("failto get regions from rms")
        return None, None
    logger.debug("got {} regions".format(len(regions)))
    keystone_ep = None
    region_name = None
    for region in regions['regions']:
        for endpoint in region['endpoints']:
            if endpoint['type'] == 'identity':
                keystone_ep = endpoint['publicURL']
                break
        if keystone_ep:
            region_name = region['name']
            break
    logger.debug("Got keystone_ep {} for region name {}".format(keystone_ep,
                                                                region_name))
    return region_name, keystone_ep


def get_token():

    logger.debug("create token")
    if not _is_authorization_enabled():
        return

    region, keystone_ep = get_keystone_ep_region_name()
    if not region or not keystone_ep:
        log_message = "fail to create token reason -- fail to get region-- " \
                      "region:{} keystone {}".format(region, keystone_ep)
        log_message = log_message.replace('\n', '_').replace('\r', '_')
        logger.error(log_message)
        return

    url = keystone_ep + '/v2.0/tokens'
    logger.debug("url :- {}".format(url))
    data = {
        "auth": {
            "tenantName": conf.authentication.tenant_name,
            "passwordCredentials": {
                "username": conf.authentication.mech_id,
                "password": conf.authentication.mech_pass
            }
        }
    }
    try:
        logger.debug("get token url- {} data= {}".format(url, data))
        respone = requests.post(url, data=json.dumps(data), headers=headers,
                                verify=conf.verify)

        if respone.status_code != 200:
            logger.error("fail to get token from url")
        logger.debug("got token for region {}".format(region))
        return region, respone.json()['access']['token']['id']

    except Exception as exp:
        logger.error(exp)
        logger.exception(exp)


def check_permissions(token_to_validate, lcp_id):
    logger.debug("Check permissions...start")
    try:
        if _is_authorization_enabled():
            token_conf = _get_token_conf()
            logger.debug("Authorization: validating token=[{}] on lcp_id=[{}]".format(token_to_validate, lcp_id))
            is_permitted = tokens.is_token_valid(token_to_validate, lcp_id, token_conf)
            logger.debug("Authorization: The token=[{}] on lcp_id=[{}] is [{}]".format(token_to_validate, lcp_id, "valid" if is_permitted else "invalid"))
        else:
            logger.debug("The authentication service is disabled. No authentication is needed.")
            is_permitted = True
    except Exception as e:
        msg = "Fail to validate request. due to {}.".format(e.message)
        logger.error(msg)
        logger.exception(e)
        is_permitted = False
    logger.debug("Check permissions...end")
    return is_permitted
