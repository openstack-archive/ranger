"""Token utility module."""
import logging
import requests

from keystoneauth1.identity import v3
from keystoneauth1 import session as ksc_session
from keystoneclient.v3 import client as v3_client
from orm.common.orm_common.utils import dictator

from pecan import request

_verify = False

OK_CODE = 200
_KEYSTONES = {}
logger = logging.getLogger(__name__)


class KeystoneNotFoundError(Exception):
    """Indicates that the Keystone EP of a certain LCP was not found."""

    pass


class TokenConf(object):
    """The Token Validator configuration class."""

    def __init__(self, mech_id, password, rms_url, tenant_name, version, user_domain_name, project_domain_name):
        """Initialize the Token Validator configuration.

        :param mech_id: Username for Keystone
        :param password: Password for Keystone
        :param rms_url: The entire RMS URL, e.g. 'http://1.3.3.7:8080'
        :param tenant_name: The ORM tenant name
        :param version: Keystone version to use (a string: '3' or '2.0')
        """
        self.mech_id = mech_id
        self.password = password
        self.rms_url = rms_url
        self.tenant_name = tenant_name
        self.version = version
        self.user_domain_name = user_domain_name
        self.project_domain_name = project_domain_name


class TokenUser(object):
    """Class with details about the token user."""

    def __init__(self, token_details, keystone_ep):
        """Initialize the Token User.

        :param token: The token object (returned by tokens.validate)
        """
        self.tenant = {}
        self.user = {}
        self.auth_url = keystone_ep
        self.token = getattr(token_details, 'auth_token', None)
        self.domain = getattr(token_details, 'project_domain_name', None)
        self.tenant['name'] = getattr(token_details, 'tenant_name', None)
        self.tenant['id'] = getattr(token_details, 'tenant_id', None)
        self.user['name'] = getattr(token_details, 'username', None)
        self.user['id'] = getattr(token_details, 'user_id', None)
        self.user['roles'] = token_details['roles']


def get_token_user(token, conf, lcp_id=None, keystone_ep=None):
    """Get a token user.

    :param token: The token to validate
    :param conf: A TokenConf object
    :param lcp_id: The ID of the LCP associated with the Keystone instance
    with which the token was created. Ignored if keystone_ep is not None
    :param keystone_ep: The Keystone endpoint, in case we already have it
    :return: False if one of the tokens received (or more) is invalid,
    True otherwise.
    """
    # Not using logger.error/exception because in some cases, these flows
    # can be completely valid
    if keystone_ep is None:
        if lcp_id is None:
            message = 'Received None for both keystone_ep and lcp_id!'
            logger.debug(message)
            raise ValueError(message)
        keystone_ep = _find_keystone_ep(conf.rms_url, lcp_id)
        if keystone_ep is None:
            message = 'Keystone EP of LCP %s not found in RMS' % (lcp_id,)
            logger.debug(message)
            logger.critical(
                'CRITICAL|CON{}KEYSTONE002|X-Auth-Region: {} is not '
                'reachable (not found in RMS)'.format(
                    dictator.get('service_name', 'ORM'), lcp_id))
            raise KeystoneNotFoundError(message)

    if conf.version == '3':
        client = v3_client
    else:
        message = 'Invalid Keystone version: %s' % (conf.version,)
        logger.debug(message)
        raise ValueError(message)

    keystone = _get_keystone_client(client, conf, keystone_ep, lcp_id)

    try:
        token_info = keystone.tokens.validate(token)
        logger.debug('User token found in Keystone')
        if not request.headers.get('X-RANGER-Requester'):
            request.headers['X-RANGER-Requester'] = \
                token_info.username

        return TokenUser(token_info, keystone_ep)
    # Other exceptions raised by validate() are critical errors,
    # so instead of returning False, we'll just let them propagate
    except client.exceptions.NotFound:
        logger.debug('User token not found in Keystone! Make sure that it is '
                     'correct and that it has not expired yet')
        return None


def _find_keystone_ep(rms_url, lcp_name):
    """Get the Keystone EP from RMS.

    :param rms_url: RMS server URL
    :param lcp_name: The LCP name
    :return: Keystone EP (string), None if it was not found
    """
    if not rms_url:
        message = 'Invalid RMS URL: %s' % (rms_url,)
        logger.debug(message)
        raise ValueError(message)

    logger.debug(
        'Looking for Keystone EP of LCP {} using RMS URL {}'.format(
            lcp_name, rms_url))

    response = requests.get('%s/v2/orm/regions?regionname=%s' % (
        rms_url, lcp_name, ), verify=_verify)
    if response.status_code != OK_CODE:
        # The LCP was not found in RMS
        logger.debug('Received bad response code from RMS: {}'.format(
            response.status_code))
        return None

    lcp = response.json()
    try:
        for endpoint in lcp['regions'][0]['endpoints']:
            if endpoint['type'] == 'identity':
                return endpoint['publicURL']
    except KeyError:
        logger.debug('Response from RMS came in an unsupported format. '
                     'Make sure that you are using RMS 3.5')
        return None

    # Keystone EP not found in the response
    logger.debug('No identity endpoint was found in the response from RMS')
    return None


def _get_keystone_client(client, conf, keystone_ep, lcp_id):
    """Get the Keystone client.

    :param client: keystoneclient package to use
    :param conf: Token conf
    :param keystone_ep: The Keystone endpoint that RMS returned
    :param lcp_id: The region ID

    :return: The instance of Keystone client to use
    """
    global _KEYSTONES
    try:
        if keystone_ep not in _KEYSTONES:
            # Instantiate the Keystone client according to the configuration
            auth = v3.Password(user_domain_name=conf.user_domain_name,
                               username=conf.mech_id,
                               password=conf.password,
                               project_domain_name=conf.project_domain_name,
                               project_name=conf.tenant_name,
                               auth_url=keystone_ep + '/v' + conf.version)
            sess = ksc_session.Session(auth=auth)
            _KEYSTONES[keystone_ep] = client.Client(session=sess)
        return _KEYSTONES[keystone_ep]
    except Exception:
        logger.critical(
            'CRITICAL|CON{}KEYSTONE001|Cannot reach Keystone EP: {} of '
            'region {}. Please contact Keystone team.'.format(
                dictator.get('service_name', 'ORM'), keystone_ep, lcp_id))
        raise
