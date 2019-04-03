"""yaml build build yaml from json input."""
import logging
from orm.services.resource_distributor.rds.services.helpers import create_final_yaml
from pecan import conf
from pprint import pformat

logger = logging.getLogger(__name__)


def yamlbuilder(alldata, region):
    logger.info("building group yaml")
    logger.debug("start building group yaml for region %s" % region['name'])
    """build group yaml.

    build yaml file from json
    :param alldata: full json data
    :param region: data per region
    :return: the full string of yaml file
    """
    logger.info("group alldata {} for region {}".format(pformat(alldata), region))

    outputs = {}
    resources = {}
    yaml_version = conf.yaml_configs.group_yaml.yaml_version
    title = {'heat_template_version': yaml_version}
    description = {'description': 'yaml file for region - %s' % region['name']}
    jsondata = alldata
    status = {"0": False, "1": True}[str(jsondata['enabled'])]

    if "roles" in alldata:
        outputs['outputs'], resources['resources'] = build_group_roles_yaml(jsondata)
    else:
        outputs['outputs'], resources['resources'] = build_group_yaml(jsondata)

    # putting all parts together for full yaml
    yamldata = create_final_yaml(title, description, resources, outputs)
    logger.debug(
        "done building group yaml for region %s " % region['name'])

    return yamldata


def build_group_yaml(jsondata):
    resources = {}
    outputs = {}
    group_name = jsondata['name']

    resources[group_name] = {
        'type': 'OS::Keystone::Group\n',
        'properties': {
            'name': "%s" % group_name,
            'description': jsondata['description'],
            'domain': jsondata['domain_name'],
            'roles': []
        }
    }

    outputs[group_name] = {
        "value": {
            "get_resource": "%s" % group_name
        }
    }

    return outputs, resources


def build_group_roles_yaml(jsondata):
    resources = {}
    outputs = {}
    group_name = jsondata['name']
    template_name = "{}-Role-Assignment".format(group_name)

    resources[template_name] = {
        'type': 'OS::Keystone::GroupRoleAssignment\n',
        'properties': {
            'group': "%s" % group_name,
            'roles': jsondata['roles']
        }
    }

    outputs[template_name] = {
        "value": {
            "get_resource": "%s" % template_name
        }
    }

    return outputs, resources
