"""unittests create customer yaml module."""
import unittest

import yaml
from mock import patch

from rds.services import yaml_customer_builder as CustomerBuild

alldata = {
    'uuid': '1e24981a-fa51-11e5-86aa-5e5517507c66',
    'metadata': [{'my_server_name': 'Apache1'}, {'ocx_cust': '123456889'}],
    'default_region': {'users': [{'id': 'userId1zzzz',
                                  'roles': ['adminzzzz', 'otherzzzzz']},
                                 {'id': 'userId2zzz',
                                  'roles': ['storagezzzzz']}],
                       'name': 'regionnamezzzz',
                       'quotas': [{'storage': {'gigabytes': '111',
                                               'volumes': '111',
                                               'snapshots': '111'},
                                   'compute': {'instances': '111',
                                               'ram': '111',
                                               'keypairs': '111',
                                               'injected_files': '111'},
                                   'network': {'port': '111',
                                               'router': '111',
                                               'subnet': '111',
                                               'network': '111',
                                               'floatingip': '111'}}]},
    'description': 'this is a description', 'enabled': 1,
    'regions': [{'users': [{'id': 'userId1', 'roles': ['admin', 'other']},
                           {'id': 'userId2', 'roles': ['storage']}],
                 'name': 'regionname', 'quotas': []},
                {'users': [], 'name': 'regionnametest',
                 'quotas': [{'storage': {'gigabytes': '10',
                                         'volumes': '10',
                                         'snapshots': '10'},
                             'compute': {'instances': '10', 'ram': '10',
                                         'keypairs': '10',
                                         'injected_files': '10'},
                             'network': {'port': '10', 'router': '10',
                                         'subnet': '10', 'network': '10',
                                         'floatingip': '10'}}]}],
    'name': 'welcome_man'}

region_quotas = {'users':
                 [],
                 'name': 'regionnametest',
                 'quotas': [{'storage': {'gigabytes': '10',
                                         'volumes': '10', 'snapshots': '10'},
                             'compute': {'instances': '10', 'ram': '10',
                                         'keypairs': '10',
                                         'injected_files': '10'},
                             'network': {'port': '10',
                                         'router': '10',
                                         'subnet': '10',
                                         'network': '10',
                                         'floatingip': '10'}}]}

region_users = {'users': [{'id': 'userId1', 'roles': ['admin', 'other']},
                          {'id': 'userId2', 'roles': ['storage']}],
                'name': 'regionname', 'quotas': []}

full_region = {'users': [{'id': 'userId1', 'roles': ['admin', 'other']},
                         {'id': 'userId2', 'roles': ['storage']}],
               'name': 'regionnametest',
               'quotas': [{'storage': {'gigabytes': '10',
                                       'volumes': '10', 'snapshots': '10'},
                           'compute': {'instances': '10', 'ram': '10',
                                       'keypairs': '10',
                                       'injected_files': '10'},
                           'network': {'port': '10', 'router': '10',
                                       'subnet': '10',
                                       'network': '10', 'floatingip': '10'}}]}


fullyaml_with_users_quotasoff = \
    'heat_template_version: 2015-1-2\n\ndescription: yaml file for region - ' \
    'regionname\n\nresources:\n  tenant_metadata:\n' \
    '    properties:\n      METADATA:\n        metadata:\n          my_server_name: Apache1\n      ' \
    '    ocx_cust: 123456889\n      TENANT_ID: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
    '    type: OS::Keystone::Metadata\n\n      \n  userId1:\n    ' \
    'properties:\n      groups:\n      - {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1_group}\n      ' \
    'name: userId1\n      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
    '        role: admin\n      - project: {get_resource: ' \
    '1e24981a-fa51-11e5-86aa-5e5517507c66}\n        role: other\n    type: OS::Keystone::User\n\n' \
    '      \n  userId2:\n    properties:\n      groups:\n      - ' \
    '{get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2_group}\n      name: userId2\n      roles:\n      ' \
    '- project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        role: storage\n' \
    '    type: OS::Keystone::User\n\n      \n  1e24981a-fa51-11e5-86aa-5e5517507c66:\n    properties:\n      ' \
    'description: this is a description\n      enabled: true\n      ' \
    'name: welcome_man\n      project_id: 1e24981a-fa51-11e5-86aa-5e5517507c66\n    type: OS::Keystone::Project2\n\n      ' \
    '\n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId1_group:\n    properties:\n      description: dummy\n      ' \
    'domain: default\n      name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1_group\n      roles:\n      - ' \
    'project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        role: {get_resource: other}\n    ' \
    'type: OS::Keystone::Group\n\n      \n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId2_group:\n    properties:\n     ' \
    ' description: dummy\n      domain: default\n      name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2_group\n      ' \
    'roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
    'role: {get_resource: storage}\n    type: OS::Keystone::Group\n\n      ' \
    '\n\noutputs:\n  userId1_id:\n    value: {get_resource: userId1}\n' \
    '  userId2_id:\n    value: {get_resource: userId2}\n  ' \
    '1e24981a-fa51-11e5-86aa-5e5517507c66_id:\n    value: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n'


fullyaml_no_users_quotasoff = \
    'heat_template_version: 2015-1-1\n\ndescription: yaml file for region ' \
    '- regionnametest\n\nresources:\n  tenant_metadata:\n    properties:\n' \
    '      METADATA:\n        metadata:\n          my_server_name: Apache1\n          ocx_cust: 123456889\n' \
    '      TENANT_ID: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n    ' \
    'type: OS::Keystone::Metadata\n\n      \n  userId1zzzz:\n    properties:\n      ' \
    'groups:\n      - {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1zzzz_group}\n      ' \
    'name: userId1zzzz\n      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
    '        role: adminzzzz\n      - ' \
    'project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        role: otherzzzzz\n' \
    '    type: OS::Keystone::User\n\n      \n  userId2zzz:\n    properties:\n      ' \
    'groups:\n      - {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2zzz_group}\n      ' \
    'name: userId2zzz\n      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
    '        role: storagezzzzz\n    type: OS::Keystone::User\n\n      ' \
    '\n  1e24981a-fa51-11e5-86aa-5e5517507c66:\n    properties:\n      description: this is a description\n' \
    '      enabled: true\n      name: welcome_man\n    ' \
    '  project_id: 1e24981a-fa51-11e5-86aa-5e5517507c66\n    type: OS::Keystone::Project2\n\n      \n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId1zzzz_group:\n    ' \
    'properties:\n      description: dummy\n      domain: default\n      ' \
    'name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1zzzz_group\n      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
    '        role: {get_resource: otherzzzzz}\n    type: OS::Keystone::Group\n\n' \
    '      \n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId2zzz_group:\n    properties:\n      description: dummy\n      ' \
    'domain: default\n      name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2zzz_group\n      roles:\n      ' \
    '- project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        role: {get_resource: storagezzzzz}\n' \
    '    type: OS::Keystone::Group\n\n      \n\noutputs:\n  userId1zzzz_id:\n' \
    '    value: {get_resource: userId1zzzz}\n  userId2zzz_id:\n    ' \
    'value: {get_resource: userId2zzz}\n  1e24981a-fa51-11e5-86aa-5e5517507c66_id:\n    ' \
    'value: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n'

full_yaml_default_quotas = 'heat_template_version: 2015-1-1\n\ndescription: yaml file for region ' \
                           '- regionname\n\nresources:\n  cinder_quota:\n    properties:\n      ' \
                           'gigabytes: 111\n      snapshots: 111\n      tenant: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
                           '      volumes: 111\n    type: OS::Cinder::Quota\n\n   ' \
                           '   \n  neutron_quota:\n    properties:\n      floatingip: 111\n' \
                           '      network: 111\n      port: 111\n      router: 111\n      subnet: 111\n' \
                           '      tenant: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n    type: OS::Neutron::Quota\n\n' \
                           '      \n  nova_quota:\n    properties:\n      injected_files: 111\n      ' \
                           'instances: 111\n      keypairs: 111\n      ram: 111\n      ' \
                           'tenant: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n    ' \
                           'type: OS::Nova::Quota\n\n      \n  tenant_metadata:\n    properties:\n      METADATA:\n      ' \
                           '  metadata:\n          my_server_name: Apache1\n          ocx_cust: 123456889\n      ' \
                           'TENANT_ID: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n    ' \
                           'type: OS::Keystone::Metadata\n\n      \n  userId1:\n' \
                           '    properties:\n      groups:\n      ' \
                           '- {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1_group}\n      name: userId1\n' \
                           '      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
                           '        role: admin\n      ' \
                           '- project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                           'role: other\n    type: OS::Keystone::User\n\n' \
                           '      \n  userId2:\n    properties:\n      groups:\n' \
                           '      - {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2_group}\n      ' \
                           'name: userId2\n      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
                           '        role: storage\n    type: OS::Keystone::User\n\n      ' \
                           '\n  1e24981a-fa51-11e5-86aa-5e5517507c66:\n    properties:\n      description: this is a description\n' \
                           '      enabled: true\n      name: welcome_man\n' \
                           '      project_id: 1e24981a-fa51-11e5-86aa-5e5517507c66\n    ' \
                           'type: OS::Keystone::Project2\n\n      \n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId1_group:\n' \
                           '    properties:\n      description: dummy\n      domain: default\n' \
                           '      name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1_group\n      roles:\n' \
                           '      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                           'role: {get_resource: other}\n    type: OS::Keystone::Group\n\n      ' \
                           '\n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId2_group:\n    properties:\n      ' \
                           'description: dummy\n      domain: default\n      name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2_group\n      ' \
                           'roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                           'role: {get_resource: storage}\n    type: OS::Keystone::Group\n\n      ' \
                           '\n\noutputs:\n  userId1_id:\n    ' \
                           'value: {get_resource: userId1}\n  userId2_id:\n    ' \
                           'value: {get_resource: userId2}\n  1e24981a-fa51-11e5-86aa-5e5517507c66_id:\n    ' \
                           'value: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n'

full_yaml_quotas = 'heat_template_version: 2015-1-1\n\ndescription: yaml file for region - ' \
                   'regionnametest\n\nresources:\n  cinder_quota:\n    ' \
                   'properties:\n      gigabytes: 10\n      snapshots: 10\n      ' \
                   'tenant: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n      volumes: 10\n    ' \
                   'type: OS::Cinder::Quota\n\n      \n  neutron_quota:\n    ' \
                   'properties:\n      floatingip: 10\n      network: 10\n      ' \
                   'port: 10\n      router: 10\n      subnet: 10\n      ' \
                   'tenant: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n    ' \
                   'type: OS::Neutron::Quota\n\n      \n  nova_quota:\n    ' \
                   'properties:\n      injected_files: 10\n      instances: 10\n      ' \
                   'keypairs: 10\n      ram: 10\n      tenant: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n    ' \
                   'type: OS::Nova::Quota\n\n      \n  tenant_metadata:\n    ' \
                   'properties:\n      METADATA:\n        metadata:\n          my_server_name: Apache1\n' \
                   '          ocx_cust: 123456889\n      TENANT_ID: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
                   '    type: OS::Keystone::Metadata\n\n      \n  userId1zzzz:\n    properties:\n      ' \
                   'groups:\n      - {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1zzzz_group}\n      ' \
                   'name: userId1zzzz\n      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
                   '        role: adminzzzz\n      - project: ' \
                   '{get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        role: ' \
                   'otherzzzzz\n    type: OS::Keystone::User\n\n      \n  ' \
                   'userId2zzz:\n    properties:\n      groups:\n      - {get_resource:' \
                   ' 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2zzz_group}\n      name: userId2zzz\n      roles:\n' \
                   '      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                   'role: storagezzzzz\n    type: OS::Keystone::User\n\n' \
                   '      \n  1e24981a-fa51-11e5-86aa-5e5517507c66:\n    properties:\n      ' \
                   'description: this is a description\n      ' \
                   'enabled: true\n      name: welcome_man\n      ' \
                   'project_id: 1e24981a-fa51-11e5-86aa-5e5517507c66\n    ' \
                   'type: OS::Keystone::Project2\n\n      \n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId1zzzz_group:\n' \
                   '    properties:\n      description: dummy\n      ' \
                   'domain: default\n      name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId1zzzz_group\n      roles:\n      ' \
                   '- project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                   'role: {get_resource: otherzzzzz}\n    type: OS::Keystone::Group\n\n' \
                   '      \n  1e24981a-fa51-11e5-86aa-5e5517507c66_userId2zzz_group:\n    properties:\n      ' \
                   'description: dummy\n      domain: default\n      name: 1e24981a-fa51-11e5-86aa-5e5517507c66_userId2zzz_group\n' \
                   '      roles:\n      - project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                   'role: {get_resource: storagezzzzz}\n    type: OS::Keystone::Group\n\n' \
                   '      \n\noutputs:\n  userId1zzzz_id:\n    ' \
                   'value: {get_resource: userId1zzzz}\n  userId2zzz_id:\n    ' \
                   'value: {get_resource: userId2zzz}\n  1e24981a-fa51-11e5-86aa-5e5517507c66_id:\n    ' \
                   'value: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n'

full_yaml_ldap = 'heat_template_version: 2015-1-2\n\ndescription: yaml file' \
                 ' for region - regionname\n\nresources:\n  tenant_metadata:\n    ' \
                 'properties:\n      METADATA:\n        metadata:\n          my_server_name: Apache1\n' \
                 '          ocx_cust: 123456889\n      TENANT_ID: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n' \
                 '    type: OS::Keystone::Metadata\n\n      \n  userId1:\n    ' \
                 'properties:\n      roles:\n      ' \
                 '- project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                 'role: admin\n      - project: ' \
                 '{get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                 'role: other\n      user: userId1\n    ' \
                 'type: OS::Keystone::UserRoleAssignment\n\n      \n  ' \
                 'userId2:\n    properties:\n      roles:\n      ' \
                 '- project: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n        ' \
                 'role: storage\n      user: userId2\n    ' \
                 'type: OS::Keystone::UserRoleAssignment\n\n      \n  ' \
                 '1e24981a-fa51-11e5-86aa-5e5517507c66:\n    properties:\n      ' \
                 'description: this is a description\n      ' \
                 'enabled: true\n      name: welcome_man\n      ' \
                 'project_id: 1e24981a-fa51-11e5-86aa-5e5517507c66\n    ' \
                 'type: OS::Keystone::Project2\n\n      \n\noutputs:\n  ' \
                 'userId1_id:\n    ' \
                 'value: {get_resource: userId1}\n  userId2_id:\n    ' \
                 'value: {get_resource: userId2}\n  1e24981a-fa51-11e5-86aa-5e5517507c66_id:\n    ' \
                 'value: {get_resource: 1e24981a-fa51-11e5-86aa-5e5517507c66}\n'


class CreateResource(unittest.TestCase):
    """class metohd."""

    @patch.object(CustomerBuild, 'conf')
    def test_create_customer_yaml_nousers(self, mock_conf):
        """test valid dict to yaml output as expected without users."""
        ver = mock_conf.yaml_configs.customer_yaml.yaml_version = '2015-1-1'
        mock_conf.yaml_configs.customer_yaml.yaml_options.quotas = False
        yamlfile = CustomerBuild.yamlbuilder(alldata, region_quotas)
        yamlfile_as_json = yaml.load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'], ver)
        self.assertEqual(yaml.load(yamlfile), yaml.load(fullyaml_no_users_quotasoff))

    @patch.object(CustomerBuild, 'conf')
    def test_create_flavor_yaml_noquotas(self, mock_conf):
        """test valid dict to yaml output as expected with users."""
        ver = mock_conf.yaml_configs.customer_yaml.yaml_version = '2015-1-2'
        mock_conf.yaml_configs.customer_yaml.yaml_options.quotas = False
        yamlfile = CustomerBuild.yamlbuilder(alldata, region_users)
        yamlfile_as_json = yaml.load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'], ver)
        self.assertEqual(yaml.load(yamlfile), yaml.load(fullyaml_with_users_quotasoff))

    @patch.object(CustomerBuild, 'conf')
    def test_create_customer_yaml_noquotas_on(self, mock_conf):
        """test valid dict to yaml output as expected with default regions."""
        ver = mock_conf.yaml_configs.customer_yaml.yaml_version = '2015-1-1'
        mock_conf.yaml_configs.customer_yaml.yaml_options.quotas = True
        yamlfile = CustomerBuild.yamlbuilder(alldata, region_users)
        yamlfile_as_json = yaml.load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'], ver)
        self.assertEqual(yaml.load(yamlfile), yaml.load(full_yaml_default_quotas))

    @patch.object(CustomerBuild, 'conf')
    def test_create_customer_yaml_withquotas_on(self, mock_conf):
        """valid dict to yaml output as expect with regions default users."""
        ver = mock_conf.yaml_configs.customer_yaml.yaml_version = '2015-1-1'
        mock_conf.yaml_configs.customer_yaml.yaml_options.quotas = True
        yamlfile = CustomerBuild.yamlbuilder(alldata, region_quotas)
        yamlfile_as_json = yaml.load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'], ver)
        self.assertEqual(yaml.load(yamlfile), yaml.load(full_yaml_quotas))

    @patch.object(CustomerBuild, 'conf')
    def test_create_flavor_yaml_ldap(self, mock_conf):
        """test valid dict to yaml output as expected with ldap system."""
        ver = mock_conf.yaml_configs.customer_yaml.yaml_version = '2015-1-2'
        mock_conf.yaml_configs.customer_yaml.yaml_options.quotas = False
        mock_conf.yaml_configs.customer_yaml.yaml_options.type = "ldap"
        yamlfile = CustomerBuild.yamlbuilder(alldata, region_users)
        yamlfile_as_json = yaml.load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'], ver)
        self.assertEqual(yaml.load(yamlfile), yaml.load(full_yaml_ldap))
