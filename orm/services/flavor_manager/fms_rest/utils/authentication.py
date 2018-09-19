import logging

from orm.common.client.keystone.keystone_utils import tokens
from orm.common.orm_common.policy import policy

from pecan import conf

logger = logging.getLogger(__name__)


def authorize(request, action):
    if not _is_authorization_enabled(conf):
        return

    auth_region = request.headers.get('X-Auth-Region')
    policy.authorize(action, request, conf)


def _is_authorization_enabled(app_conf):
    return app_conf.authentication.enabled


def get_token_conf(app_conf):
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


def check_permissions(app_conf, token_to_validate, lcp_id):
    logger.debug("Check permissions...start")
    try:
        if _is_authorization_enabled(app_conf):
            if token_to_validate is not None and lcp_id is not None and str(token_to_validate).strip() != '' and str(lcp_id).strip() != '':
                token_conf = get_token_conf(app_conf)
                logger.debug("Authorization: validating token=[{}] on lcp_id=[{}]".format(token_to_validate, lcp_id))
                is_permitted = tokens.is_token_valid(token_to_validate, lcp_id, token_conf)
                logger.debug("Authorization: The token=[{}] on lcp_id=[{}] is [{}]"
                             .format(token_to_validate, lcp_id, "valid" if is_permitted else "invalid"))
            else:
                raise Exception("Token=[{}] and/or Region=[{}] are empty/none.".format(token_to_validate, lcp_id))
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
