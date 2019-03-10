"""unittests create group yaml module."""
from mock import patch
import unittest
import yaml

from orm.services.resource_distributor.rds.services import yaml_group_builder as GroupBuild

alldata = {
    'domain_name': 'nc',
    'description': 'this is a description', 'enabled': 1,
    'regions': [{'name': 'regionname'}],
    'name': 'test_group'}

yaml_group = \
    'heat_template_version: 2015-1-1\n\ndescription: yaml file for region - ' \
    'regionname\n\nresources:\n'\
    '  test_group:\n    properties:\n'\
    '      description: "this is a description"\n'\
    '      domain: nc\n'\
    '      name: test_group\n      roles: []\n'\
    '    type: OS::Keystone::Group\n\n\n'\
    'outputs:\n'\
    '  test_group:\n'\
    '    value: {get_resource: test_group}\n'

region = {'name': 'regionname',
               'rangerAgentVersion': 1.0}

class CreateResource(unittest.TestCase):
    """class metohd."""
    maxDiff = None

    @patch.object(GroupBuild, 'conf')
    def test_create_group_yaml_nousers(self, mock_conf):
        """test valid dict to yaml output as expected without users."""
        ver = mock_conf.yaml_configs.group_yaml.yaml_version = '2015-1-1'
        yamlfile = GroupBuild.yamlbuilder(alldata, region)
        yamlfile_as_json = yaml.safe_load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'], ver)
        self.assertEqual(yaml.safe_load(yamlfile), yaml.safe_load(yaml_group))

