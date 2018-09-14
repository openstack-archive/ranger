"""Policy Engine For ORM."""

import logging

from orm.common.client.keystone.keystone_utils import tokens
from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import dictator
import qolicy
from wsme.exc import ClientSideError

logger = logging.getLogger(__name__)
_ENFORCER = None
_POLICY_FILE = None
_TOKEN_CONF = None


def reset():
    global _ENFORCER
    if _ENFORCER:
        _ENFORCER.clear()
        _ENFORCER = None

    global _POLICY_FILE
    if _POLICY_FILE:
        _POLICY_FILE = None


class EnforcerError(Exception):
    """An exception that receives *args and **kwargs, necessary for
    Enforcer.enforce().
    """
    def __init__(self, *args, **kwargs):
        super(EnforcerError, self).__init__()


def _get_rules_from_file(path):
    logger.debug('Reading policy file: {}'.format(path))

    return qolicy.Rules.load_json(open(path, 'r').read(), 'default')


def init(policy_file, token_conf, default_rule=None):
    """Init an Enforcer class.

       :param policy_file: Custom policy file to use.
       :param default_rule: Default rule to use
       :param token_conf: The Keystone utils token configuration
    """
    logger.info('Initializing policy enforcer...')

    global _ENFORCER
    global _POLICY_FILE
    global _TOKEN_CONF
    if not _ENFORCER:
        loaded_rules = _get_rules_from_file(policy_file)
        _POLICY_FILE = policy_file
        _TOKEN_CONF = token_conf
        _ENFORCER = qolicy.Enforcer(None,
                                    policy_file=None,
                                    rules=loaded_rules,
                                    default_rule=default_rule,
                                    use_conf=False)


def reset_rules(overwrite=True, use_conf=False):
    """Reset rules based on the provided dict of rules.

       :param rules: New rules to use. It should be an instance of dict.
       :param overwrite: Whether to overwrite current rules or update them
                         with the new rules.
       :param use_conf: Whether to reload rules from config file.
    """
    if not _POLICY_FILE:
        message = 'Policy file not set (did you call policy.init?)'
        logger.error(message)
        raise ValueError(message)
    _ENFORCER.set_rules(_get_rules_from_file(_POLICY_FILE),
                        overwrite, use_conf)


def enforce(action, token, user, lcp_id=None, keystone_ep=None,
            do_raise=True):
    """Verifies that the action is valid on the target in this context.

       :param action: string representing the action to be checked
           this should be colon separated for clarity.
           i.e. ``compute:create_instance``,
           ``compute:attach_volume``,
           ``volume:attach_volume``
       :param token: The token to validate
       :param lcp_id: The ID of the LCP associated with the Keystone instance
           with which the token was created
       :param keystone_ep: The Keystone endpoint, in case we already have it
       :param do_raise: if True (the default), raises Unauthorized (401);
           if False, returns False

       :raises EnforcerError if verification fails and do_raise is True.

       :return: returns a non-False value (not necessarily "True") if
           authorized, and the exact value False if not authorized and
           do_raise is False.
    """
    logger.debug('Enforcing policy - action: {}, token: {}, lcp_id: {}, '
                 'keystone_ep: {}'.format(action, token, lcp_id, keystone_ep))
    # Re-read the rules, in case the policy file has changed
    reset_rules()

    # May raise EnforcerError, we'll let it propagate
    result = _ENFORCER.enforce(action, {}, user, do_raise=do_raise,
                               exc=EnforcerError, action=action)

    return result


def _is_authorization_enabled(app_conf):
    return app_conf.authentication.enabled


def authorize(action, request, app_conf, keystone_ep=None):
    """Authorize a request.

    :param action: The requested action, in the policy.json syntax
    :param request: Pecan request object
    :param app_conf: Application configuration
    :param keystone_ep: Keystone endpoint, in case we already have it

    :raises Unauthorized (401) in case anything fails in the authorization
        process
    """
    logger.info('Authorize...start')

    token_to_validate = request.headers.get('X-Auth-Token')
    lcp_id = request.headers.get('X-Auth-Region')

    keystone_ep = keystone_ep if keystone_ep else (
        request.headers.get('Keystone-Endpoint'))

    try:
        if _is_authorization_enabled(app_conf):
            try:
                # Set the service name for Nagios codes
                dictator.soft_set('service_name', app_conf.server.name.upper())

                user = tokens.get_token_user(token_to_validate, _TOKEN_CONF,
                                             lcp_id, keystone_ep)
                request.headers['X-RANGER-Client'] = user.user['name']
                request.headers['X-RANGER-Owner'] = user.tenant['id']
                request.headers['Keystone-Endpoint'] = user.auth_url
                keystone_ep = user.auth_url                  
            except Exception:
                user = None
                request.headers['X-RANGER-Client'] = 'NA'
                logger.exception(
                    "policy - Failed to get_token_user, using user={}".format(
                        user))

            if token_to_validate is not None and lcp_id is not None and str(token_to_validate).strip() != '' and str(lcp_id).strip() != '':
                logger.debug('Authorization: enforcing policy on token=[{}], lcp_id=[{}]'.format(token_to_validate, lcp_id))
                enforce(action, token_to_validate, user, lcp_id, keystone_ep)
                is_permitted = True
                logger.debug('Authorization: policy check passed')
            else:
                logger.debug('Token=[{}] and/or Region=[{}] are empty/none.'.format(token_to_validate, lcp_id))
                logger.info(
                    'INFO|CON{}AUTH004|One or more of the authentication headers are missing'.format(
                        dictator.get('service_name', 'ORM')))
                # Enforce anyway, in case the policy for this is to always
                # allow any user to perform this operation
                enforce(action, token_to_validate, user)
                is_permitted = True
        else:
            logger.debug('The authentication service is disabled. No authentication is needed.')
            is_permitted = True
    except ClientSideError as e:
        logger.error('Fail to validate request. due to {}.'.format(e.message))
        raise err_utils.get_error('N/A', status_code=e.code)
    except EnforcerError:
        logger.error('The token is unauthorized according to the policy')
        is_permitted = False
    except Exception as e:
        msg = 'Fail to validate request. due to {}.'.format(e.message)
        logger.error(msg)
        logger.exception(e)
        is_permitted = False

    logger.info('Authorize...end')
    if not is_permitted:
        raise err_utils.get_error('N/A', status_code=401)
