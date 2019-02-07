"""yaml build build yaml from json input."""
import logging
import re
import yaml

from pecan import conf

logger = logging.getLogger(__name__)


def get_users_quotas(data, region):
    """get users and quotas from region

    :param data:
    :param region:
    :return:
    """
    users = region['users'] if region['users'] else data['default_region']['users']
    quotas = region['quotas'] if region['quotas'] else data['default_region']['quotas']
    return users, quotas


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


def _metadata_to_tags(metadata):

    return '[' + ','.join(
        str(k) + '=' + str(v) for i in metadata for k, v in i.iteritems()) + ']'


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
    # enclose project_description in double quotes to prevent yaml parsing issues
    # when special characters are encountered
    project_description = '"%s"' % (jsondata['description'])
    # TODO(amar): remove these lines when using objects instead of string json
    status = {"0": False, "1": True}[str(jsondata['enabled'])]
    outputs['outputs'] = {}
    resources['resources'] = {}

    resources['resources']["%s" % alldata['uuid']] =\
        {'type': 'OS::Keystone::Project\n',
         'properties': {'name': "%s" % project_name,
                        'project_id': alldata['uuid'],
                        'description': project_description,
                        'tags': _metadata_to_tags(alldata['metadata']),
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

    # adjust_resource = CMSAdjustResource(region['rangerAgentVersion'])
    adjust_resource = CMSAdjustResource()
    adjust_resource.fix_quota_resource_item(alldata['uuid'], quotas, resources, options)

    # putting all parts together for full yaml
    yamldata = create_final_yaml(title, description, resources, outputs)
    logger.debug(
        "done building customer yaml for region %s " % region['name'])
    return yamldata


class CMSAdjustResource():
    # def __init__(self, rangerAgentVersion):
        # if rangerAgentVersion:
        #    self.adjust_quota_parameters = CMSAdjustQuotaResource().adjust_quota_parameters
    def __init__(self):
        self.adjust_quota_parameters = CMSAdjustQuotaResource().adjust_quota_parameters

    def fix_quota_resource_item(self, uuid, quotas, resources, options):
        if conf.yaml_configs.customer_yaml.yaml_options.quotas:
            quotas_keys = dict(conf.yaml_configs.customer_yaml.yaml_keys.quotas_keys)
            for items in quotas:
                for item in items:

                    # rename quota keys as needed
                    for quota_item in items[item].keys()[:]:
                        if quota_item in quotas_keys:
                            items[item][quotas_keys[quota_item]] = items[item][quota_item]
                            new_quota_item_key = quotas_keys[quota_item]
                            del items[item][quota_item]
                            quota_item = new_quota_item_key

                        self.adjust_quota_parameters(quota_item, items[item])

                    # adding project to each quota
                    items[item]['project'] = \
                        "{'get_resource': %s}" % uuid
                    resources['resources'][options[item][0]] = \
                        {"type": options[item][1], "properties": items[item]}


class CMSAdjustQuotaResource():

    def __init__(self):
        self.unsupported_quotas = conf.yaml_configs.customer_yaml.cms_quota.resource_quotas.quota_unsupported_params

    def adjust_quota_parameters(self, key, item):
        if key in self.unsupported_quotas:
            del item[key]
            logger.warning("Region does not support Quota Parameter {}."
                           " removed from resource".format(key))
