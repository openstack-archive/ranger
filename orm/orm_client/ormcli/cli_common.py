import config
import json
import requests

OK_CODE = 200

ORM_CLIENT_KWARGS = {'type': str, 'help': 'client name', 'default': None,
                     'nargs': '?'}


class MissingArgumentError(Exception):
    """Should be raised when an argument was found missing by CLI logic."""
    pass


def get_keystone_ep(rms_url, region_name):
    """Get the Keystone EP from RMS.

    :param rms_url: RMS server URL
    :param region_name: The region name
    :return: Keystone EP (string), None if it was not found
    """
    try:
        response = requests.get('%s/v2/orm/regions?regionname=%s' % (
            rms_url, region_name, ), verify=config.verify)
    except requests.exceptions.ConnectionError as e:
        print('Could not connect to RMS, URL: {}'.format(rms_url))
        return None

    if response.status_code != OK_CODE:
        print('RMS returned status: {}, content: {}'.format(
            response.status_code, response.content))
        return None

    # RMS returned 200
    lcp = response.json()
    try:
        for endpoint in lcp['regions'][0]['endpoints']:
            if endpoint['type'] == 'identity':
                return endpoint['publicURL']
    except KeyError:
        print('Response from RMS came in an unsupported format. '
              'Make sure that you are using RMS 3.5')
        return None

    # Keystone EP not found in the response
    print('No identity endpoint was found in the response from RMS')
    return None


def pretty_print_json(json_to_print):
    """Print a json without the u' prefix."""
    print(json.dumps(json_to_print))
