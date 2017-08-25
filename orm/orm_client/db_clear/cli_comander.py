import config as conf
import json
import logging
import os


log = logging.getLogger(__name__)


def _get_regions(customer):
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


def _build_get_customer_cli_command(resource_id):
    cli_command = """get_customer %s""" % resource_id
    log.debug('cli command {}'.format(cli_command))
    return cli_command


def _get_customer_regions(cli_command, service):
    client_header = service.upper()
    log.debug("get customer with cli")
    os.chdir(conf.cli_dir)
    cwd = os.getcwd()
    customer = os.popen('./orm %s %s ' % (service.lower(), cli_command))
    log.debug("got cusmer with cli ... check if got regions")
    return _get_regions(customer.read())


def get_resource_regions(resource_id, service):
    log.debug("---ORM CLI---")
    regions = None
    if service.upper() == 'CMS':
        regions = _get_customer_regions(
            _build_get_customer_cli_command(resource_id), service)
    return regions
