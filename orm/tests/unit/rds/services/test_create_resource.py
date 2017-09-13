"""create resource unittest module."""
import unittest

from mock import patch
from orm.services.resource_distributor.rds.services import resource as ResourceService
from orm.services.resource_distributor.rds.services.model.region_resource_id_status import (Model,
                                                          ResourceMetaData,
                                                          StatusModel)

result = Model(
    status="success", timestamp="123456789", region="name",
    transaction_id=5, resource_id="1",
    ord_notifier="", err_msg="123", err_code="12", operation="create",
    resource_extra_metadata=[ResourceMetaData(checksum=1, virtual_size=2, size=3)]
)

uuid = "uuid-12345"


class InputData(object):
    """mock class."""

    def __init__(self, resource_id, resource_type,
                 targets, operation="create",
                 transaction_id="", model="",
                 external_transaction_id=""):
        """init function.

        : param resource_id:
        : param resource_type:
        : param targets:
        : param operation:
        : param transaction_id:
        : param model:
        : param external_transaction_id:
        """
        self.resource_id = resource_id
        self.targets = targets
        self.resource_type = resource_type
        self.operation = operation
        self.transaction_id = transaction_id
        self.model = model
        self.external_transaction_id = external_transaction_id


class SoT(object):
    """mock class."""

    def save_resource_to_sot(*args):
        """mock function."""
        return None

    def delete_resource_from_sot(*args):
        """mock function."""
        return None


class CreateResource(unittest.TestCase):
    """create resource test."""

    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id',
    #               return_value=StatusModel(status=[result]))
    # def test_create_customer_conflict_rise(self, result):
    #     """check raise conflict."""
    #     with self.assertRaises(ResourceService.ConflictValue):
    #         ResourceService.main(jsondata, uuid, 'customer', 'create')

    # @patch.object(ResourceService, '_upload_to_sot', return_value=[1, 2])
    # @patch.object(ResourceService, '_create_data_to_sot', return_value=[1, 2])
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id', return_value=None)
    # @patch.object(ResourceService.uuid_utils,
    #               'get_random_uuid', return_value='uuid-gen-123456')
    # def test_create_customer_valid_uuid_gen(self, tranid, result,
    #                                         sotdata, sotupload):
    #     """check flow with uuid gen."""
    #     status_model = StatusModel(status=[result])
    #     status_model.regions = None
    #     result.return_value = status_model
    #     resource_id = ResourceService.main(jsondata, uuid,
    #                                        'customer', 'create')
    #     self.assertEqual(resource_id, jsondata['uuid'])

    @patch.object(ResourceService.regionResourceIdStatus, 'add_status',
                  return_value=None)
    @patch.object(ResourceService, '_upload_to_sot', return_value=[1, 2])
    @patch.object(ResourceService, '_create_data_to_sot', return_value=[1, 2])
    @patch.object(ResourceService.regionResourceIdStatus,
                  'get_regions_by_status_resource_id', return_value=None)
    @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
                  side_effect=Exception("uuid general exception"))
    def test_create_customer_not_valid_uuid_gen(self, tranid, result, sotdata,
                                                sotupload, database):
        """uuid gen raise an error."""
        status_model = StatusModel(status=[result])
        status_model.regions = None
        result.return_value = status_model
        with self.assertRaises(ResourceService.ErrorMesage):
            resource_id = ResourceService.main(jsondata, uuid,
                                               'customer', 'create')

    # @patch.object(ResourceService.regionResourceIdStatus, 'add_status',
    #               return_value=None)
    # @patch.object(ResourceService.yaml_customer_builder, 'yamlbuilder',
    #               return_value=["anystring"])
    # @patch.object(ResourceService, '_upload_to_sot', return_value=[1, 2])
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id', return_value=None)
    # @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
    #               return_value='uuid-gen-123456')
    # def test_create_customer_sot_data(self, tranid, result, sotupload,
    #                                   yamlbuilder, database):
    #     """check sot data build for customer."""
    #     status_model = StatusModel(status=[result])
    #     status_model.regions = None
    #     result.return_value = status_model
    #     resource_id = ResourceService.main(jsondata, uuid,
    #                                        'customer', 'create')

    # @patch.object(ResourceService.regionResourceIdStatus, 'add_status',
    #               return_value=None)
    # @patch.object(ResourceService.yaml_customer_builder, 'yamlbuilder',
    #               return_value=["anystring"])
    # @patch.object(ResourceService.sot_factory, 'get_sot',
    #               return_value=SoT())
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id', return_value=None)
    # @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
    #               return_value='uuid-gen-123456')
    # def test_create_resource_upload_sot(self, tranid, result, sotupload,
    #                                     yamlbuilder, database):
    #     """check upload to sot."""
    #     status_model = StatusModel(status=[result])
    #     status_model.regions = None
    #     result.return_value = status_model
    #     resource_id = ResourceService.main(jsondata, uuid,
    #                                        'customer', 'create')

    # @patch.object(ResourceService.regionResourceIdStatus, 'add_status',
    #               return_value=None)
    # @patch.object(ResourceService.yaml_flavor_bulder, 'yamlbuilder',
    #               return_value=["anystring"])
    # @patch.object(ResourceService.sot_factory, 'get_sot', return_value=SoT())
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id', return_value=None)
    # @patch.object(ResourceService.uuid_utils,
    #               'get_random_uuid', return_value='uuid-gen-123456')
    # def test_create_flavor_sot_data(self, tranid, result, sotupload,
    #                                 yamlbuilder, database):
    #     """check flavor data create."""
    #     status_model = StatusModel(status=[result])
    #     status_model.regions = None
    #     result.return_value = status_model
    #     resource_id = ResourceService.main(flavorjsondata, uuid,
    #                                        'flavor', 'create')

    @patch.object(ResourceService.regionResourceIdStatus,
                  'add_status', return_value=None)
    @patch.object(ResourceService.yaml_customer_builder,
                  'yamlbuilder', return_value=["anystring"])
    @patch.object(ResourceService.sot_factory, 'get_sot', return_value=SoT())
    @patch.object(ResourceService.regionResourceIdStatus,
                  'get_regions_by_status_resource_id', return_value=None)
    @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
                  return_value='uuid-gen-123456')
    def test_create_flavor_sot_data_check(self, tranid, result, sotupload,
                                          yamlbuilder, database):
        """check list creating."""
        input_data = InputData(
            transaction_id='497ab942-1ac0-11e6-82f3-005056a5129b',
            resource_type='customer',
            resource_id='1e24981a-fa51-11e5-86aa-5e5517507c66',
            operation='create',
            targets=targets
        )
        status_model = StatusModel(status=[result])
        status_model.regions = None
        result.return_value = status_model
        result = ResourceService._create_data_to_sot(input_data)
        self.assertEqual(result, target_list)

    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id',
    #               return_value=StatusModel(status=[result]))
    # def test_delete_flavor_conflict(self, databasemock):
    #     """check delete flavor with conflict."""
    #     with self.assertRaises(ResourceService.ConflictValue):
    #         ResourceService.main(flavorjsondata, uuid, 'flavor', 'delete')

    @patch.object(ResourceService.regionResourceIdStatus,
                  'add_status', return_value=None)
    @patch.object(ResourceService, '_upload_to_sot', return_value=[1, 2])
    @patch.object(ResourceService, '_create_data_to_sot', return_value=[1, 2])
    @patch.object(ResourceService.regionResourceIdStatus,
                  'get_regions_by_status_resource_id', return_value=None)
    @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
                  side_effect=Exception("uuid general exception"))
    def test_delete_flavor_not_valid_uuid_gen(self, tranid, result, sotdata,
                                              sotupload, database):
        """delete flavor uuid gen raise an error."""
        status_model = StatusModel(status=[result])
        status_model.regions = None
        result.return_value = status_model
        with self.assertRaises(ResourceService.ErrorMesage):
            resource_id = ResourceService.main(flavorjsondata, uuid,
                                               'flavor', 'delete')

    # @patch.object(ResourceService.yaml_flavor_bulder,
    #               'yamlbuilder', return_value=["anystring"])
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'add_status', return_value=None)
    # # @patch.object(ResourceService, '_delete_from_sot', return_value = None)
    # @patch.object(ResourceService.sot_factory, 'get_sot', return_value=SoT())
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id', return_value=None)
    # @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
    #               return_value='uuid-gen-123456')
    # def test_delete_flavor_not_valid_all(self, tranid, result,
    #                                      sotdata, sotupload, yaml_mock):
    #     """delete flavor uuid gen raise an error."""
    #     status_model = StatusModel(status=[result])
    #     status_model.regions = None
    #     result.return_value = status_model
    #     resource_id = ResourceService.main(flavorjsondata, uuid,
    #                                        'flavor', 'delete')
    #     self.assertEqual('uuid-uuid-uuid-uuid', resource_id)

    # @patch.object(ResourceService.regionResourceIdStatus, 'add_status',
    #               return_value=None)
    # @patch.object(ResourceService.yaml_customer_builder, 'yamlbuilder',
    #               return_value=["anystring"])
    # @patch.object(ResourceService.sot_factory, 'get_sot',
    #               return_value=SoT())
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id', return_value=None)
    # @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
    #               return_value='uuid-gen-123456')
    # def test_create_resource_up2load_sot_put(self, moc_get_random_uuid,
    #                                          moc_get_regions_by_status_resource_id,
    #                                          moc_get_sot,
    #                                          moc_yamlbuilder, moc_add_status):
    #     """check upload to sot."""
    #     status_model = StatusModel(status=[result])
    #     status_model.regions = None
    #     moc_get_regions_by_status_resource_id.return_value = status_model
    #     resource_id = ResourceService.main(jsondata, uuid,
    #                                        'customer', 'modify')

    # @patch.object(ResourceService.regionResourceIdStatus, 'add_status',
    #               return_value=None)
    # @patch.object(ResourceService.yaml_image_builder, 'yamlbuilder',
    #               return_value=["anystring"])
    # @patch.object(ResourceService.sot_factory, 'get_sot',
    #               return_value=SoT())
    # @patch.object(ResourceService.regionResourceIdStatus,
    #               'get_regions_by_status_resource_id', return_value=None)
    # @patch.object(ResourceService.uuid_utils, 'get_random_uuid',
    #               return_value='uuid-gen-123456')
    # def test_create_resource_up2load_sot_put_image(self, moc_get_random_uuid,
    #                                          moc_get_regions_by_status_resource_id,
    #                                          moc_get_sot,
    #                                          moc_yamlbuilder, moc_add_status):
    #     """check upload to sot."""
    #     status_model = StatusModel(status=[result])
    #     status_model.regions = None
    #     moc_get_regions_by_status_resource_id.return_value = status_model
    #     resource_id = ResourceService.main(json_data_image, uuid,
    #                                        'image', 'modify')

    def test_get_inputs_from_resource_type(self):
        input_data = ResourceService._get_inputs_from_resource_type(jsondata,
                                                                    'customer',
                                                                    'uuid-12345')
        assert (input_data.__dict__ == input_data_resource)

    def test_get_inputs_from_resource_type_image(self):
        input_data = ResourceService._get_inputs_from_resource_type(json_data_image,
                                                                    'image',
                                                                    'uuid-12345')
        assert (input_data.__dict__ == expected_image_input_data)

    def test_unknown_resource_type(self):
        with self.assertRaises(ResourceService.ErrorMesage):
            input_data = ResourceService._get_inputs_from_resource_type(jsondata,
                                                                        'unknown',
                                                                        'uuid-12345')


jsondata = {
    "uuid": "1e24981a-fa51-11e5-86aa-5e5517507c66", "default_region":
        {
            "quotas":
                [
                    {
                        "compute": {
                            "instances": "10",
                            "ram": "10",
                            "keypairs": "10",
                            "injected_files": "10"
                        },
                        "storage": {"gigabytes": "10",
                                    "snapshots": "10",
                                    "volumes": "10"
                                    },
                        "network": {
                            "router": "10",
                            "floatingip": "10",
                            "port": "10",
                            "network": "10",
                            "subnet": "10"
                        }}],
            "users":
                [
                    {
                        "id": "userId1zzzz",
                        "roles":
                            [
                                "adminzzzz",
                                "otherzzzzz"
                            ]
                    },
                    {"id": "userId2zzz",
                     "roles":
                         [
                             "storagezzzzz"
                         ]
                     }
                ],
            "name": "regionnamezzzz",
            "action": "delete",
        },
    "description": "this is a description",
    "enabled": 1,
    "regions":
        [
            {
                "quotas":
                    [],
                "users":
                    [
                        {
                            "id": "userId1",
                            "roles":
                                [
                                    "admin",
                                    "other"
                                ]
                        },
                        {"id": "userId2",
                         "roles":
                             [
                                 "storage"
                             ]
                         }
                    ],
                "name": "regionname",
                "action": "create"
            },
            {
                "quotas":
                    [
                        {
                            "compute":
                                {
                                    "instances": "10",
                                    "ram": "10",
                                    "keypairs": "10",
                                    "injected_files": "10"
                                },
                            "storage":
                                {
                                    "gigabytes": "10",
                                    "snapshots": "10",
                                    "volumes": "10"
                                },
                            "network":
                                {
                                    "router": "10",
                                    "floatingip": "10",
                                    "port": "10",
                                    "network": "10",
                                    "subnet": "10"
                                }
                        }
                    ],
                "users":
                    [],
                "name": "regionnametest",
                "action": "delete"
            }
        ],
    "name": "welcome_man"
}

flavorjsondata = {
    "status": "complete",
    "profile": "P2",
    "regions": [
        {
            "name": "North1",
            "action": "create"
        },
        {
            "name": "North2",
            "action": "delete"
        }
    ],
    "description": "First flavor for AMAR",
    "ram": 64,
    "visibility": "public",
    "extra_specs": {
        "key1": "value1",
        "key2": "value2",
        "keyx": "valuex"
    },
    "vcpus": 2,
    "swap": 0,
    "tenants": [
        {
            "tenant_id": "abcd-efgh-ijkl-4567"
        },
        {
            "tenant_id": "abcd-efgh-ijkl-4567"
        }
    ],
    "disk": 512,
    "empheral": 1,
    "id": "uuid-uuid-uuid-uuid",
    "name": "Nice Flavor"
}

json_data = {
    "uuid": "1e24981a-fa51-11e5-86aa-5e5517507c66",
    "default_region": {
        "users": [
            {
                "id": "userId1zzzz",
                "roles": [
                    "adminzzzz",
                    "otherzzzzz"
                ]
            },
            {
                "id": "userId2zzz",
                "roles": [
                    "storagezzzzz"
                ]
            }
        ],
        "name": "regionnamezzzz",
        "action": "create",
        "quotas": [
            {
                "storage": {
                    "gigabytes": "111",
                    "volumes": "111",
                    "snapshots": "111"
                },
                "compute": {
                    "instances": "111",
                    "ram": "111",
                    "keypairs": "111",
                    "injected_files": "111"
                },
                "network": {
                    "port": "111",
                    "router": "111",
                    "subnet": "111",
                    "network": "111",
                    "floatingip": "111"
                }
            }
        ]
    },
    "description": "this is a description",
    "enabled": 1,
    "regions": [
        {
            "users": [
                {
                    "id": "userId1",
                    "roles": [
                        "admin",
                        "other"
                    ]
                },
                {
                    "id": "userId2",
                    "roles": [
                        "storage"
                    ]
                }
            ],
            "name": "regionname",
            "action": "delete",
            "quotas": []
        },
        {
            "users": [],
            "name": "regionnametest",
            "action": "modify",
            "quotas": [
                {
                    "storage": {
                        "gigabytes": "10",
                        "volumes": "10",
                        "snapshots": "10"
                    },
                    "compute": {
                        "instances": "10",
                        "ram": "10",
                        "keypairs": "10",
                        "injected_files": "10"
                    },
                    "network": {
                        "port": "10",
                        "router": "10",
                        "subnet": "10",
                        "network": "10",
                        "floatingip": "10"
                    }
                }
            ]
        }
    ],
    "name": "welcome_man"
}

target_list = [{'template_data': ['anystring'],
                'operation': 'create',
                'resource_name': '1e24981a-fa51-11e5-86aa-5e5517507c66',
                'region_id': 'regionname', 'resource_type': u'customer'},
               {'template_data': 'delete', 'operation': 'delete',
                'resource_name': '1e24981a-fa51-11e5-86aa-5e5517507c66',
                'region_id': 'regionnametest', 'resource_type': u'customer'}]

targets = [{'users': [{'id': 'userId1', 'roles': ['admin', 'other']},
                      {'id': 'userId2', 'roles': ['storage']}],
            'name': 'regionname', "action": "create", 'quotas': []},
           {'users': [],
            'name': 'regionnametest',
            "action": "delete",
            'quotas': [{'storage': {'gigabytes': '10', 'volumes': '10',
                                    'snapshots': '10'},
                        'compute': {'instances': '10', 'ram': '10',
                                    'keypairs': '10', 'injected_files': '10'},
                        'network': {'port': '10',
                                    'router': '10',
                                    'subnet': '10',
                                    'network': '10',
                                    'floatingip': '10'}}]}]

json_data_image = {
    "internal_id": 1,
    "id": "uuu1id12-uuid-uuid-uuid",
    "name": "Ubuntu",
    "enabled": 1,
    "protected": 1,
    "url": "https://mirrors.it.att.com/images/image-name",
    "visibility": "public",
    "disk_format": "raw",
    "container_format": "bare",
    "min_disk": 2,
    "min_ram": 0,
    "regions": [
        {
            "name": "North",
            "type": "single",
            "action": "delete",
            "image_internal_id": 1
        },
        {
            "name": "North",
            "action": "create",
            "type": "single",
            "image_internal_id": 1
        }
    ],
    "image_properties": [
        {
            "key_name": "Key1",
            "key_value": "Key1.value",
            "image_internal_id": 1
        },
        {
            "key_name": "Key2",
            "key_value": "Key2.value",
            "image_internal_id": 1
        }
    ],
    "image_tenant": [
        {
            "tenant_id": "abcd-efgh-ijkl-4567",
            "image_internal_id": 1
        },
        {
            "tenant_id": "abcd-efgh-ijkl-4567",
            "image_internal_id": 1
        }
    ],
    "image_tags": [
        {
            "tag": "abcd-efgh-ijkl-4567",
            "image_internal_id": 1
        },
        {
            "tag": "abcd-efgh-ijkl-4567",
            "image_internal_id": 1
        }
    ],
    "status": "complete",
}

input_data_resource = {'resource_id': '1e24981a-fa51-11e5-86aa-5e5517507c66',
                       'targets': [
                           {'action': 'create', 'quotas': [],
                            'name': 'regionname',
                            'users': [
                                {'id': 'userId1', 'roles': ['admin', 'other']},
                                {'id': 'userId2', 'roles': ['storage']}]},
                           {'action': 'delete',
                            'quotas': [{
                                'storage': {
                                    'gigabytes': '10',
                                    'volumes': '10',
                                    'snapshots': '10'},
                                'compute': {
                                    'instances': '10',
                                    'ram': '10',
                                    'keypairs': '10',
                                    'injected_files': '10'},
                                'network': {
                                    'subnet': '10',
                                    'router': '10',
                                    'port': '10',
                                    'network': '10',
                                    'floatingip': '10'}}],
                            'name': 'regionnametest',
                            'users': []}],
                       'resource_type': 'customer',
                       'model': {
                           'uuid': '1e24981a-fa51-11e5-86aa-5e5517507c66',
                           'default_region': {'action': 'delete',
                                              'quotas': [{'storage': {
                                                  'gigabytes': '10',
                                                  'volumes': '10',
                                                  'snapshots': '10'},
                                                  'compute': {
                                                      'instances': '10',
                                                      'ram': '10',
                                                      'keypairs': '10',
                                                      'injected_files': '10'},
                                                  'network': {
                                                      'subnet': '10',
                                                      'router': '10',
                                                      'port': '10',
                                                      'network': '10',
                                                      'floatingip': '10'}}],
                                              'name': 'regionnamezzzz',
                                              'users': [
                                                  {'id': 'userId1zzzz',
                                                   'roles': ['adminzzzz',
                                                             'otherzzzzz']},
                                                  {'id': 'userId2zzz',
                                                   'roles': [
                                                       'storagezzzzz']}]},
                           'description': 'this is a description',
                           'enabled': 1, 'regions': [
                               {'action': 'create', 'quotas': [],
                                'name': 'regionname',
                                'users': [{'id': 'userId1',
                                           'roles': ['admin', 'other']},
                                          {'id': 'userId2',
                                           'roles': ['storage']}]},
                               {'action': 'delete',
                                'quotas': [{'storage': {'gigabytes': '10',
                                                        'volumes': '10',
                                                        'snapshots': '10'},
                                            'compute': {'instances': '10',
                                                        'ram': '10',
                                                        'keypairs': '10',
                                                        'injected_files': '10'},
                                            'network': {'subnet': '10',
                                                        'router': '10',
                                                        'port': '10',
                                                        'network': '10',
                                                        'floatingip': '10'}}],
                                'name': 'regionnametest', 'users': []}],
                           'name': 'welcome_man'},
                       'external_transaction_id': 'uuid-12345',
                       'operation': 'create',
                       'transaction_id': ''}

expected_image_input_data = {
    'resource_id': 'uuu1id12-uuid-uuid-uuid',
    'targets': [
        {
            'action': 'delete', 'image_internal_id': 1,
            'type': 'single', 'name': 'North'},
        {
            'action': 'create', 'image_internal_id': 1,
            'type': 'single', 'name': 'North'}],
    'resource_type': 'image',
    'model': {
        'status': 'complete', 'name': 'Ubuntu',
        'internal_id': 1,
        'url': 'https://mirrors.it.att.com/images/image-name',
        'disk_format': 'raw', 'min_ram': 0,
        'enabled': 1, 'visibility': 'public',
        'image_tags': [
            {'image_internal_id': 1, 'tag': 'abcd-efgh-ijkl-4567'},
            {'image_internal_id': 1, 'tag': 'abcd-efgh-ijkl-4567'}],
        'regions': [
            {
                'action': 'delete', 'image_internal_id': 1,
                'type': 'single', 'name': 'North'},
            {
                'action': 'create', 'image_internal_id': 1,
                'type': 'single', 'name': 'North'}],
        'image_properties': [
            {
                'key_name': 'Key1',
                'key_value': 'Key1.value',
                'image_internal_id': 1},
            {
                'key_name': 'Key2',
                'key_value': 'Key2.value',
                'image_internal_id': 1}],
        'protected': 1, 'image_tenant': [
            {'tenant_id': 'abcd-efgh-ijkl-4567', 'image_internal_id': 1},
            {'tenant_id': 'abcd-efgh-ijkl-4567', 'image_internal_id': 1}],
        'container_format': 'bare',
        'min_disk': 2,
        'id': 'uuu1id12-uuid-uuid-uuid'},
    'external_transaction_id': 'uuid-12345',
    'operation': 'create', 'transaction_id': ''}
