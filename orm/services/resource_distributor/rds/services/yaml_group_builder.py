"""yaml build build yaml from json input."""
import logging
import re
import yaml

from pecan import conf

logger = logging.getLogger(__name__)


def create_final_yaml(title, description, resources, outputs):
    """put all yaml strings together.

    :param title: ther version of yaml
    :param description: file description
    :param resources: body of the yaml file
    :param outputs: the output of the yaml
    :return: the full string of yaml file
    """
    title_yaml = re.sub("'", "", yaml.dump(title, default_flow_style=False))
    description_yaml = yaml.dump(description, default_flow_style=False)
    resourcesyaml = re.sub("''", '', yaml.dump(resources,
                                               default_flow_style=False))
    resources_yaml = re.sub("'", '', resourcesyaml)
    yamldata = title_yaml
    yamldata = yamldata + "\n" + description_yaml
    yamldata = yamldata + "\n" + resources_yaml
    yamldata = yamldata + "\n" + yaml.dump(outputs)
    return yamldata


def yamlbuilder(alldata, region):
    logger.info("building group yaml")
    logger.debug("start building group yaml for region %s" % region['name'])
    """build group yaml.

    build yaml file from json
    :param alldata: full json data
    :param region: data per region
    :return: the full string of yaml file
    """
    outputs = {}
    resources = {}
    yaml_version = conf.yaml_configs.group_yaml.yaml_version
    title = {'heat_template_version': yaml_version}
    description = {'description': 'yaml file for region - %s' % region['name']}
    jsondata = alldata
    group_name = jsondata['name']
    group_description = '"%s"' % (jsondata['description'])
    status = {"0": False, "1": True}[str(jsondata['enabled'])]
    outputs['outputs'] = {}
    resources['resources'] = {}

    resources['resources'][group_name] =\
        {'type': 'OS::Keystone::Group\n',
         'properties': {'name': "%s" % group_name,
                        'description': group_description,
                        'domain': alldata['domain_name'],
                        'roles': []}}

    # create the output
    outputs['outputs'][group_name] =\
        {"value": {"get_resource": "%s" % group_name}}

    # putting all parts together for full yaml
    yamldata = create_final_yaml(title, description, resources, outputs)
    logger.debug(
        "done building group yaml for region %s " % region['name'])
    return yamldata


