import config as conf
import json
import logging
import os
import subprocess

log = logging.getLogger(__name__)


def _get_cms_regions(customer):
    regions = []
    try:
        customer_json = json.loads(customer)
        if 'regions' not in customer_json:
            raise Exception("got bad response from orm cli ")
        for region in customer_json['regions']:
            regions.append(region['name'])
    except Exception as exp:
        raise Exception("got bad response from orm cli {}".format(exp.message))
    message = "got no regions from orm cli"
    if regions:
        message = "got regions from orm cli --{}--".format(regions)
    log.debug(message)
    return regions


def _get_flavor_regions(flavor):
    regions = []

    try:
        flavor_json = json.loads(flavor)
        if 'regions' not in flavor_json['flavor']:
            raise Exception("got bad response from orm cli ")
        for region in flavor_json['flavor']['regions']:
            regions.append(region['name'])
    except Exception as exp:
        raise Exception("got bad response from orm cli {}".format(exp.message))

    message = "got no regions from orm cli"
    if regions:
        message = "got regions from orm cli --{}--".format(regions)
    log.debug(message)
    return regions


def _get_image_regions(image):
    regions = []
    try:
        image_json = json.loads(image)
        if 'regions' not in image_json['image']:
            raise Exception("got bad response from orm cli ")
        for region in image_json['image']['regions']:
            regions.append(region['name'])
    except Exception as exp:
        raise Exception("got bad response from orm cli {}".format(exp.message))
    message = "got no regions from orm cli"
    if regions:
        message = "got regions from orm cli --{}--".format(regions)
    log.debug(message)
    return regions


def get_resource_regions(resource_id, service):
    regions = None

    client_header = service.upper()
    os.chdir(conf.cli_dir)
    cwd = os.getcwd()
    log.debug("---ORM CLI---")

    if service.upper() == 'CMS':
        log.debug("get customer with cli")
        cli_command = """get_customer %s""" % resource_id
        log.debug('cli command {}'.format(cli_command))
        cmd = 'python orm %s %s ' % (service.lower(), cli_command)
        customer = subprocess.check_output(cmd.split(), shell=False)
        log.debug("got customer with cli ... check if got regions")

        return _get_cms_regions(customer)

    elif service.upper() == 'FMS':
        log.debug("get flavor with cli")
        cli_command = """get_flavor %s""" % resource_id
        log.debug('cli command {}'.format(cli_command))
        cmd = 'python orm %s %s ' % (service.lower(), cli_command)
        log.debug("got flavor with cli ... check if got regions")
        flavor = subprocess.check_output(cmd.split(), shell=False)

        return _get_flavor_regions(flavor)

    elif service.upper() == 'IMS':
        log.debug("get image with cli")
        cli_command = """get_image %s""" % resource_id
        log.debug('cli command {}'.format(cli_command))
        cmd = 'python orm %s %s ' % (service.lower(), cli_command)
        log.debug("got image with cli ... check if got regions")
        flavor = subprocess.check_output(cmd.split(), shell=False)

        return _get_image_regions(flavor)
