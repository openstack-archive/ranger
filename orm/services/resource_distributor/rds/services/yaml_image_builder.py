import logging
from pecan import conf
import re
import uuid
import yaml

my_logger = logging.getLogger(__name__)


def create_full_yaml(title, resources, description, outputs):
    title_yaml = re.sub("'", "", yaml.dump(title, default_flow_style=False))
    description_yaml = yaml.dump(description, default_flow_style=False)
    resources_yaml = re.sub("'", '', re.sub("''", '', yaml.dump(resources, default_flow_style=False)))
    outputs_yaml = re.sub("'", '', re.sub("''", '', yaml.dump(outputs)))
    full_yaml = title_yaml + "\n" + description_yaml
    full_yaml = full_yaml + "\n" + resources_yaml + "\n" + outputs_yaml
    return full_yaml


def _properties(alldata, region):
    public = True if alldata['visibility'] == "public" else False
    protected = {0: False, 1: True}[alldata['protected']]
    tenants = [tenant['customer_id'] for tenant in alldata['customers']]
    properties = dict(
        name=alldata['name'],
        container_format=alldata["container_format"],
        min_ram=alldata['min_ram'],
        disk_format=alldata['disk_format'],
        min_disk=alldata['min_disk'],
        id=str(uuid.UUID(alldata['id'])),
        protected=protected,
        copy_from=alldata["url"],
        owner=alldata["owner"],
        is_public=public,
        tenants=str(tenants)
    )
 
    import pdb; pdb.set_trace()
    if region['action'] <> 'create':
        properties['deactivate'] = {1: False, 0: True}[alldata['enabled']]

    if alldata['properties']:
        properties['extra_properties'] = alldata['properties']

    return properties


def _glanceimage(alldata, region):
    return dict(
        type="OS::Glance::Image2",
        properties=_properties(alldata, region)
    )


def yamlbuilder(alldata, region):
    resources = {}
    outputs = {}
    image_type = "glance_image"
    yaml_version = conf.yaml_configs.image_yaml.yaml_version
    title = {'heat_template_version': yaml_version}
    description = {'description': 'yaml file for region - %s' % region['name']}
    resources['resources'] = {"glance_image": _glanceimage(alldata, region)}
    outputs['outputs'] = {
        '%s_id' % image_type: {"value": {"get_resource": "%s" % image_type}}}
    full_yaml = create_full_yaml(title, resources, description, outputs)
    return full_yaml
