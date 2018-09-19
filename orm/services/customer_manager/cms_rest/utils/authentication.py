import logging

from orm.common.client.keystone.keystone_utils import tokens
from orm.common.orm_common.policy import policy
from orm.common.orm_common.utils import api_error_utils as err_utils
from pecan import conf

logger = logging.getLogger(__name__)


def authorize(request, action):
    if not _is_authorization_enabled(conf):
        return

    auth_region = request.headers.get('X-Auth-Region')
    if not auth_region:
        raise err_utils.get_error('N/A', message='X-Auth-Region is missing',
                                  status_code=401)
    policy.authorize(action, request, conf)


def _is_authorization_enabled(app_conf):
    return app_conf.authentication.enabled


def _get_token_conf(app_conf):
    mech_id = app_conf.authentication.mech_id
    mech_password = app_conf.authentication.mech_pass
    rms_url = app_conf.authentication.rms_url
    tenant_name = app_conf.authentication.tenant_name
    keystone_version = app_conf.authentication.keystone_version
    user_domain_name = app_conf.authentication.user_domain_name
    project_domain_name = app_conf.authentication.project_domain_name
    conf = tokens.TokenConf(mech_id, mech_password, rms_url, tenant_name,
                            keystone_version, user_domain_name, project_domain_name)
    return conf
