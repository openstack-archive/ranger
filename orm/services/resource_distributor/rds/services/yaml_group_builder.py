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

    outputs = {"outputs": {}}
    resources = {"resources": {}}
    yaml_version = conf.yaml_configs.group_yaml.yaml_version
    title = {'heat_template_version': yaml_version}
    description = {'description': 'yaml file for region - %s' % region['name']}
    jsondata = alldata
    group_name = jsondata['name']

    resources["resources"][group_name] = {
        'type': 'OS::Keystone::Group\n',
        'properties': {
            'name': "%s" % group_name,
            'description': jsondata['description'],
            'domain': jsondata['domain_name']
        }
    }

    if len(jsondata["groups_roles"]) > 0:

        template_name = "{}-Role-Assignment".format(group_name)
        roles = [] 
        for customer_role in jsondata["groups_customer_roles"]:
            roles.append({
                "role": customer_role["role_name"],
                "project": customer_role["customer_uuid"]
            })

        for domain_role in jsondata["groups_domain_roles"]:
            roles.append({
                "role": domain_role["role_name"],
                "domain": domain_role["domain_name"]
            })

        resources["resources"][template_name] = {
            'type': 'OS::Keystone::GroupRoleAssignment\n',
            'properties': {
                'group': "%s" % group_name,
                'roles': roles
            }
        } 
        outputs["outputs"][template_name + "_id"] = {
            "value": {
                "get_resource": "%s" % template_name
            }
        }

    outputs["outputs"][group_name + "_id"] = {
        "value": {
            "get_resource": "%s" % group_name
        }
    }

    # putting all parts together for full yaml
    yamldata = create_final_yaml(title, description, resources, outputs)
    logger.debug(
        "done building group yaml for region %s " % region['name'])

    return yamldata
