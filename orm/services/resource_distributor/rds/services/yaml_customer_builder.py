"""yaml build build yaml from json input."""
import logging
import re
import yaml

from pecan import conf

logger = logging.getLogger(__name__)

def get_users_quotas(data, region):
    """get default or own region.

    get users and quotas from default or actual region
    :param data:
    :param region:
    :return:
    """
    users = region['users']
    quotas = region['quotas']
    if not users:
        users = data['default_region']['users']
    if not quotas:
        quotas = data['default_region']['quotas']
    return users, quotas


def creat_final_yaml(title, description, resources, outputs):
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
    yamldata = yamldata + "\n"+description_yaml
    yamldata = yamldata + "\n"+resources_yaml
    yamldata = yamldata + "\n"+yaml.dump(outputs)
    return yamldata


def _create_metadata_yaml(alldata):
    metadata ={}
    metadata_items={}
    for item in alldata['metadata']:
        metadata_items.update(item)
    metadata['tenant_metadata'] = {'type': 'OS::Keystone::Metadata\n',
                                   'properties': {
                                       'TENANT_ID': "{'get_resource': '%s'}" %
                                                    alldata['uuid'],
                                       'METADATA': {
                                           'metadata': metadata_items}}}
    return metadata


def yamlbuilder(alldata, region):
    logger.info("building customer yaml")
    logger.debug("start building flavor yaml for region %s" % region['name'])
    """build cstomer yaml.

    build yaml file from json
    :param alldata: full json data
    :param region: data per region
    :return: the full string of yaml file
    """
    outputs = {}
    resources = {}
    yaml_version = conf.yaml_configs.customer_yaml.yaml_version
    yaml_type = conf.yaml_configs.customer_yaml.yaml_options.type
    title = {'heat_template_version': yaml_version}
    description = {'description': 'yaml file for region - %s' % region['name']}
    jsondata = alldata
    project_name = jsondata['name']
    project_description = jsondata['description']
    # TODO(amar): remove these lines when using objects instead of string json
    status = {"0": False, "1": True}[str(jsondata['enabled'])]
    outputs['outputs'] = {}
    resources['resources'] = {}
    resources['resources']["%s" % alldata['uuid']] =\
        {'type': 'OS::Keystone::Project2\n',
         'properties': {'name': "%s" % project_name,
                        'project_id': alldata['uuid'],
                        'description': project_description,
                        'enabled': status}}
    # create the output
    outputs['outputs']["%s_id" % alldata['uuid']] =\
        {"value": {"get_resource": "%s" % alldata['uuid']}}

    users, quotas = get_users_quotas(alldata, region)
    for user in users:
        user_roles = []
        any_role = []
        for role in user['roles']:
            role_format = "%s"
            user_roles.append(
                {"role": role_format % role,
                 'project': "{'get_resource': '%s'}" % alldata['uuid']}
            )
            # create the output for roles
          #  outputs['outputs']["%s_id" % role] =\
         #       {"value": {"get_resource": "%s" % role}}

        # no support for group when type is ldap
        if yaml_type != 'ldap':
            # create one group for user
            # not real group its only from heat to be able to delete the user
            any_role = [
                {'project': "{'get_resource': '%s'}" % alldata['uuid'],
                 'role': "{'get_resource': '%s'}" % role}
            ]
            group_name = "%s_%s_group" % (alldata['uuid'], user['id'])
            resources['resources'][group_name] = \
                {'type': 'OS::Keystone::Group\n',
                 'properties': {'name': "%s" % group_name,
                                'domain': 'default',
                                'description': 'dummy',
                                'roles': any_role}}

            # remove groupe section when type is ldap
            # create users :: added the hard coded groupe
            user_group = ["{'get_resource': '%s'}" % group_name]
            resources['resources'][user['id']] = \
                {'type': 'OS::Keystone::User\n',
                 'properties': {'name': user['id'],
                                'groups': user_group,
                                'roles': user_roles}}
        else:
            resources['resources'][user['id']] = \
                {'type': 'OS::Keystone::UserRoleAssignment\n',
                 'properties': {'user': user['id'],
                                'roles': user_roles}}

        # create the output for users
        outputs['outputs']["%s_id" % user['id']] = \
            {"value": {"get_resource": user['id']}}

    options = {"compute": ["nova_quota", "OS::Nova::Quota\n"],
               "network": ["neutron_quota", "OS::Neutron::Quota\n"],
               "storage": ["cinder_quota", "OS::Cinder::Quota\n"]}

    # create quotas if quotas
    if conf.yaml_configs.customer_yaml.yaml_options.quotas:
        quotas_keys = dict(conf.yaml_configs.customer_yaml.yaml_keys.quotas_keys)
        for items in quotas:
            for item in items:

                # these lines added to check if got excpected keys if not they will be replaced
                for ite in items[item].keys()[:]:
                    if ite in quotas_keys:
                        items[item][quotas_keys[ite]] = items[item][ite]
                        del items[item][ite]
                #------------------------------------

                # adding tenant to each quota
                items[item]['tenant'] = \
                    "{'get_resource': %s}" % alldata['uuid']
                resources['resources'][options[item][0]] = \
                    {"type": options[item][1], "properties": items[item]}
    metadata = _create_metadata_yaml(alldata)
    resources['resources'].update(metadata)
    # putting all parts together for full yaml
    yamldata = creat_final_yaml(title, description, resources, outputs)
    logger.debug(
        "done building customer yaml for region %s " % region['name'])
    return yamldata
