"""Token utility module."""
import logging
import requests

from keystoneclient.auth.identity import v3
from keystoneclient import session as ksc_session
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

    def __init__(self, mech_id, password, rms_url, tenant_name, version):
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
                token_info.user['username']

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


def _does_user_have_role(keystone, version, user, role, location):
    """Check whether a user has a role.

    :param keystone: The Keystone client to use
    :param version: Keystone version
    :param user: A dict that represents the user in question
    :param role: The role to check whether the user has
    :param location: Keystone role location
    :return: True if the user has the requested role, False otherwise.
    :raise: client.exceptions.NotFound when the requested role does not exist,
    ValueError when the version is 2.0 but the location is not 'tenant'
    """
    location = dict(location)
    if version == '3':
        role = keystone.roles.find(name=role)
        try:
            return keystone.roles.check(role, user=user['user']['id'],
                                        **location)
        except exceptions.NotFound:
            return False
        except KeyError:
            # Shouldn't be raised when using Keystone's v3/v2.0 API, but let's
            #  play on the safe side
            logger.debug('The user parameter came in a wrong format!')
            return False


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


def is_token_valid(token_to_validate, lcp_id, conf, required_role=None,
                   role_location=None):
    """Validate a token.

    :param token_to_validate: The token to validate
    :param lcp_id: The ID of the LCP associated with the Keystone instance
    with which the token was created
    :param conf: A TokenConf object
    :param required_role: The required role for privileged actions,
    e.g. 'admin' (optional).
    :param role_location: The Keystone role location (a dict whose single
    key is either 'domain' or 'tenant', whose value is the location name)
    :return: False if one of the tokens received (or more) is invalid,
    True otherwise.
    :raise: KeystoneNotFoundError when the Keystone EP for the required LCP
    was not found in RMS output,
    client.exceptions.AuthorizationFailure when the connection with the
    Keystone EP could not be established,
    client.exceptions.EndpointNotFound when _our_ authentication
    (as an admin) with Keystone failed,
    ValueError when an invalid Keystone version was specified,
    ValueError when a role or a tenant was not found,
    ValueError when a role is required but role_location is None.
    """
    keystone_ep = _find_keystone_ep(conf.rms_url, lcp_id)
    if keystone_ep is None:
        raise KeystoneNotFoundError('Keystone EP of LCP %s not found in RMS' %
                                    (lcp_id,))

    if conf.version == '3':
        client = v3_client
    else:
        raise ValueError('Invalid Keystone version: %s' % (conf.version,))

    keystone = _get_keystone_client(client, conf, keystone_ep, lcp_id)

    try:
        user = keystone.tokens.validate(token_to_validate)
        logger.debug('User token found in Keystone')
    # Other exceptions raised by validate() are critical errors,
    # so instead of returning False, we'll just let them propagate
    except client.exceptions.NotFound:
        logger.debug('User token not found in Keystone! Make sure that it is'
                     'correct and that it has not expired yet')
        return False

    if required_role is not None:
        if role_location is None:
            raise ValueError(
                'A role is required but no role location was specified!')

        try:
            logger.debug('Checking role...')
            return _does_user_have_role(keystone, conf.version, user,
                                        required_role, role_location)
        except client.exceptions.NotFound:
            raise ValueError('Role %s or tenant %s not found!' % (
                required_role, role_location,))
    else:
        # We know that the token is valid and there's no need to enforce a
        # policy on this operation, so we can let the user pass
        logger.debug('No role to check, authentication finished successfully')
        return True