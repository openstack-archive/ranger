import requests

from pecan import conf


def get_random_uuid():
    response = requests.post(conf.UUID_URL, verify=conf.verify)
    return response.json()['uuid']
