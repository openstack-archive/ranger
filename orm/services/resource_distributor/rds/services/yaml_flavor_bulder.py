"""flavor builder module."""
import logging
import re

import yaml

from pecan import conf

my_logger = logging.getLogger(__name__)


def create_final_yaml(title, resources, description, outputs):
    """connect yaml strings together."""
    title_yaml = re.sub("'", "", yaml.dump(title, default_flow_style=False))
    description_yaml = yaml.dump(description, default_flow_style=False)
    resources_yaml = yaml.dump(resources)
    outputs_yaml = yaml.dump(outputs)
    yamldata = title_yaml + "\n" + description_yaml
    yamldata = yamldata + "\n" + resources_yaml + "\n" + outputs_yaml
    return yamldata


def yamlbuilder(alldata, region):
    """build yaml."""
    my_logger.info("building flavor yaml")
    my_logger.debug("start building flavor yaml for region %s" % region['name'])
    resources = {}
    extra_specs = {}
    outputs = {}
    tags = {}
    options = {}
    tenants = []
    flavor_type = 'nova_flavor'
    rxtx_factor = conf.yaml_configs.flavor_yaml.yaml_args.rxtx_factor
    if 'rxtx_factor' in alldata:
        rxtx_factor = int(alldata['rxtx_factor'])
    yaml_version = conf.yaml_configs.flavor_yaml.yaml_version
    public = {'public': True, 'private': False}[alldata['visibility']]
    title = {'heat_template_version': yaml_version}
    description = {'description': 'yaml file for region - %s' % region['name']}
    ram = int(alldata['ram'])
    swap = int(alldata['swap'])
    for key, value in alldata['extra_specs'].items():
        extra_specs[key] = value
    # Handle tags
    if 'tag' in alldata:
        for key, value in alldata['tag'].items():
            extra_specs[key] = value
    # Handle options
    if 'options' in alldata:
        for key, value in alldata['options'].items():
            extra_specs[key] = value
    # Handle tenants
    for tenant in alldata['tenants']:
        tenants.append(tenant['tenant_id'])

    # Generate the output
    resources['resources'] = {}
    resources['resources'][flavor_type] = \
        {'type': 'OS::Nova::Flavor',
         'properties': {'disk': alldata['disk'],
                        'ephemeral': alldata['ephemeral'],
                        'extra_specs': extra_specs,
                        'flavorid': alldata['id'],
                        'is_public': public,
                        'name': alldata['name'],
                        'ram': ram,
                        'rxtx_factor': rxtx_factor,
                        'swap': swap,
                        'tenants': tenants,
                        'vcpus': alldata['vcpus']}}
    # gen the output
    outputs['outputs'] = {}
    outputs['outputs']['%s_id' % flavor_type] =\
        {'value': {"get_resource": flavor_type}}
    flavor_yaml = create_final_yaml(title, resources, description, outputs)
    my_logger.debug(
        "done!!! building flavor yaml for region %s " % region['name'])
    return flavor_yaml
