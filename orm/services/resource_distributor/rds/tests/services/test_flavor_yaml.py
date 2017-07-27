"""flavor unittest module."""
from mock import patch
from rds.services import yaml_flavor_bulder as FlavorBuild
import unittest
import yaml


alldata = {'status': 'complete', 'series': 'P2',
           'description': 'First flavor for AMAR',
           'ephemeral': 1, 'ram': 64, 'visibility': 'public',
           'regions': [{'name': 'North1'}, {'name': 'North2'}], 'vcpus': 2,
           'extra_specs': {'key2:aa': 'value2', 'key1': 'value1',
                           'keyx': 'valuex'},
           'tag': {'tagkey2': 'tagvalue2', 'tagkey1': 'tagvalue1'},
           'options': {'optkey2': 'optvalue2', 'optkey1': 'optvalue1'},
           'swap': 51231, 'disk': 512,
           'tenants': [{'tenant_id': 'abcd-efgh-ijkl-4567'},
                       {'tenant_id': 'abcd-efgh-ijkl-4567'}],
           'id': 'uuid-uuid-uuid-uuid',
           'name': 'Nice Flavor'}

region = {'name': '0'}


fullyaml = 'heat_template_version: 2015-1-1\n\ndescription: yaml file for region - 0\n\nresources:\n' \
           '  nova_flavor:\n    properties:\n      disk: 512\n      ephemeral: 1\n' \
           '      extra_specs: {key1: value1, "key2:aa": value2, keyx: valuex, tagkey1: tagvalue1, ' \
           'tagkey2: tagvalue2, optkey1: optvalue1, optkey2: optvalue2}\n' \
           '      flavorid: uuid-uuid-uuid-uuid\n' \
           '      is_public: true\n      name: Nice Flavor\n      ram: 64\n      rxtx_factor: 1\n' \
           '      swap: 51231\n      tenants: [abcd-efgh-ijkl-4567, abcd-efgh-ijkl-4567]\n      vcpus: 2\n' \
           '    type: OS::Nova::Flavor\n\n      \n\noutputs:\n  nova_flavor_id:\n' \
           '    value: {get_resource: nova_flavor}\n'

alldata_rxtffactor = {'status': 'complete', 'series': 'P2',
                      'description': 'First flavor for AMAR',
                      'ephemeral': 1, 'ram': 64, 'visibility': 'public',
                      'regions': [{'name': 'North1'}, {'name': 'North2'}],
                      'vcpus': 2,
                      'extra_specs': {'key2': 'value2', 'key1': 'value1',
                                      'keyx': 'valuex'},
                      'tag': {'tagkey2': 'tagvalue2', 'tagkey1': 'tagvalue1'},
                      'options': {'optkey2': 'optvalue2', 'optkey1': 'optvalue1'},
                      'swap': 51231, 'disk': 512,
                      'tenants': [{'tenant_id': 'abcd-efgh-ijkl-4567'},
                                  {'tenant_id': 'abcd-efgh-ijkl-4567'}],
                      'id': 'uuid-uuid-uuid-uuid',
                      'rxtx_factor': 10,
                      'name': 'Nice Flavor'}

fullyaml_rxtx = 'heat_template_version: 2015-1-1\n\ndescription: yaml file for region - 0\n\nresources:\n' \
                '  nova_flavor:\n    properties:\n      disk: 512\n      ephemeral: 1\n' \
                '      extra_specs: {key1: value1, key2: value2, keyx: valuex, tagkey1: tagvalue1, ' \
                'tagkey2: tagvalue2, optkey1: optvalue1, optkey2: optvalue2}\n' \
                '      flavorid: uuid-uuid-uuid-uuid\n' \
                '      is_public: true\n      name: Nice Flavor\n      ram: 64\n      rxtx_factor: 10\n' \
                '      swap: 51231\n      tenants: [abcd-efgh-ijkl-4567, abcd-efgh-ijkl-4567]\n      vcpus: 2\n' \
                '    type: OS::Nova::Flavor\n\n      \n\noutputs:\n  nova_flavor_id:\n' \
                '    value: {get_resource: nova_flavor}\n'


class CreateResource(unittest.TestCase):
    """class method flavor tests."""

    @patch.object(FlavorBuild, 'conf')
    def test_create_flavor_yaml(self, mock_conf):
        self.maxDiff = None
        """test valid dict to yaml output as expected."""
        mock_conf.yaml_configs.flavor_yaml.yaml_version = '2015-1-1'
        mock_conf.yaml_configs.flavor_yaml.yaml_args.rxtx_factor = 1
        yamlfile = FlavorBuild.yamlbuilder(alldata, region)
        yamlfile_as_json = yaml.load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'],
                         mock_conf.yaml_configs.flavor_yaml.yaml_version)
        self.assertEqual(yaml.load(fullyaml), yamlfile_as_json)

    @patch.object(FlavorBuild, 'conf')
    def test_create_flavor_yaml_(self, mock_conf):
        self.maxDiff = None
        """test when extx ioncluded in the input."""
        mock_conf.yaml_configs.flavor_yaml.yaml_version = '2015-1-1'
        mock_conf.yaml_configs.flavor_yaml.yaml_args.rxtx_factor = 1
        yamlfile = FlavorBuild.yamlbuilder(alldata_rxtffactor, region)
        yamlfile_as_json = yaml.load(yamlfile)
        self.assertEqual(yamlfile_as_json['heat_template_version'],
                         mock_conf.yaml_configs.flavor_yaml.yaml_version)
        self.assertEqual(yaml.load(fullyaml_rxtx), yamlfile_as_json)
