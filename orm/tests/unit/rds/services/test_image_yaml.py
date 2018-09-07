from mock import patch
import unittest
import yaml

from orm.services.resource_distributor.rds.services import yaml_image_builder as ImageBuild

json_input = {
    'status': 'complete', 'name': 'Ubuntu', 'internal_id': 1,
    'url': 'https://mirrors.it.att.com/images/image-name',
    'disk_format': 'raw', 'min_ram': 0, 'enabled': 1,
    'visibility': 'public', 'owner': 'unknown',
    'image_tags': [{
        'image_internal_id': 1, 'tag': 'abcd-efgh-ijkl-4567'
    }, {
        'image_internal_id': 1, 'tag': 'abcd-efgh-ijkl-4567'
    }],
    'regions': [{
        'action': 'delete', 'image_internal_id': 1,
        'type': 'single', 'name': 'North'
    }, {
        'action': 'create', 'image_internal_id': 1,
        'type': 'single', 'name': 'North'
    }],
    'properties': {
        'key_name': 'Key1', 'key_value': 'Key1.value',
        'image_internal_id': 1
    },
    'protected': 1,
    'customers': [{
        'customer_id': 'abcd-efgh-ijkl-4567', 'image_id': 1
    }, {
        'customer_id': 'abcd-efgh-ijkl-4567', 'image_id': 1
    }],
    'container_format': 'bare', 'min_disk': 2,
    'id': '12345678901234567890123456789012'
}

region = {'action': 'delete', 'image_internal_id': 1, 'type': 'single',
          'name': 'North'}

yaml_output = {
    'description': 'yaml file for region - North',
    'resources': {
        'glance_image': {
            'properties': {
                'container_format': 'bare', 'disk_format': 'raw',
                'is_public': True,
                'copy_from': 'https://mirrors.it.att.com/images/image-name',
                'min_disk': 2, 'min_ram': 0, 'name': 'Ubuntu', 'owner': 'unknown',
                'protected': True,
                'id': '12345678-9012-3456-7890-123456789012',
                'tenants': ['abcd-efgh-ijkl-4567', 'abcd-efgh-ijkl-4567'],
                'extra_properties': {
                    'key_name': 'Key1', 'key_value': 'Key1.value',
                    'image_internal_id': 1
                }
            },
            'type': 'OS::Glance::Image'
        }
    },
    'heat_template_version': '2015-1-1',
    'outputs': {
        'glance_image_id': {
            'value': {
                'get_resource': 'glance_image'
            }
        }
    }
}


class CreateImage(unittest.TestCase):
    """class method image test."""

    @patch.object(ImageBuild, 'conf')
    def test_create_image(self, mock_conf):
        self.maxDiff = None
        mock_conf.yaml_configs.image_yaml.yaml_version = '2015-1-1'
        response = ImageBuild.yamlbuilder(json_input, region)
        self.assertEqual(yaml.safe_load(response), yaml_output)
