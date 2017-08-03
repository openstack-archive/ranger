import logging

from keystone_utils import tokens
from orm_common.policy import policy
from pecan import conf
from rms.services import services as RegionService

logger = logging.getLogger(__name__)


def _get_keystone_ep(auth_region):
    result = RegionService.get_region_by_id_or_name(auth_region)
    for ep in result.endpoints:
        if ep.type == 'identity':
            return ep.publicurl

    # Keystone EP not found
    return None


def authorize(request, action):
    if not _is_authorization_enabled(conf):
        return

    auth_region = request.headers.get('X-Auth-Region')
    try:
        keystone_ep = _get_keystone_ep(auth_region)
    except Exception:
        # Failed to find Keystone EP - we'll set it to None instead of failing
        # because the rule might be to let everyone pass
        keystone_ep = None

    policy.authorize(action, request, conf, keystone_ep=keystone_ep)


def _is_authorization_enabled(app_conf):
    return app_conf.authentication.enabled


def get_token_conf(app_conf):
    mech_id = app_conf.authentication.mech_id
    mech_password = app_conf.authentication.mech_pass
    # RMS URL is not necessary since this service is RMS
    rms_url = ''
    tenant_name = app_conf.authentication.tenant_name
    keystone_version = app_conf.authentication.keystone_version
    conf = tokens.TokenConf(mech_id, mech_password, rms_url, tenant_name,
                            keystone_version)
    return conf
