import unittest
from mock import patch
from rds.services import yaml_image_builder as ImageBuild
import yaml
import datetime

json_input = {'status': 'complete', 'name': 'Ubuntu', 'internal_id': 1,
              'url': 'https://mirrors.it.att.com/images/image-name',
              'disk_format': 'raw', 'min_ram': 0, 'enabled': 1,
              'visibility': 'public', 'owner': 'unknown', 'image_tags': [
        {'image_internal_id': 1, 'tag': 'abcd-efgh-ijkl-4567'},
        {'image_internal_id': 1, 'tag': 'abcd-efgh-ijkl-4567'}], 'regions': [
        {'action': 'delete', 'image_internal_id': 1, 'type': 'single',
         'name': 'North'},
        {'action': 'create', 'image_internal_id': 1, 'type': 'single',
         'name': 'North'}], 'image_properties': [
        {'key_name': 'Key1', 'key_value': 'Key1.value',
         'image_internal_id': 1},
        {'key_name': 'Key2', 'key_value': 'Key2.value',
         'image_internal_id': 1}], 'protected': 1, 'customers': [
        {'customer_id': 'abcd-efgh-ijkl-4567', 'image_id': 1},
        {'customer_id': 'abcd-efgh-ijkl-4567', 'image_id': 1}],
              'container_format': 'bare', 'min_disk': 2,
              'id': 'uuu1id12-uuid-uuid-uuid'}

region = {'action': 'delete', 'image_internal_id': 1, 'type': 'single',
          'name': 'North'}

yaml_output = {'description': 'yaml file for region - North',
 'resources': {'glance_image': {'properties': {'container_format': 'bare',
    'disk_format': 'raw',
    'is_public': True,
    'copy_from': 'https://mirrors.it.att.com/images/image-name',
    'min_disk': 2,
    'min_ram': 0,
    'name': 'North',
    'owner': 'unknown',
    'protected': True,
    'tenants': ['abcd-efgh-ijkl-4567', 'abcd-efgh-ijkl-4567']},
   'type': 'OS::Glance::Image2'}},
 'heat_template_version': '2015-1-1',
 'outputs': {'glance_image_id': {'value': {'get_resource': 'glance_image'}}}}

class CreateImage(unittest.TestCase):
    """class method image test."""

    @patch.object(ImageBuild, 'conf')
    def test_create_image(self, mock_conf):
        self.maxDiff = None
        mock_conf.yaml_configs.image_yaml.yaml_version = '2015-1-1'
        response = ImageBuild.yamlbuilder(json_input, region)
        self.assertEqual(yaml.load(response), yaml_output)
