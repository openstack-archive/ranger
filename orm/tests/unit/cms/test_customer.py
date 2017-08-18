import requests

from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer import root
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model import Models
from orm.tests.unit.cms import FunctionalTest, test_utils
import mock
import sqlalchemy
from wsme.exc import ClientSideError

customer_logic_mock = None


class TestCustomerController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        root.authentication = mock.MagicMock()

        root.CustomerLogic = get_mock_customer_logic
        root.CustomerLogic.return_error = 0

        root.utils = mock.MagicMock()
        root.utils.make_transid.return_value = 'some_trans_id'
        root.utils.audit_trail.return_value = None
        root.utils.make_uuid.return_value = 'some_uuid'

        root.err_utils = mock.MagicMock()

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_create_customer(self):
        # given
        requests.post = mock.MagicMock(return_value=ResponseMock(201))

        # when
        response = self.app.post_json('/v1/orm/customers', CUSTOMER_JSON)

        # assert
        assert response.status_int == 201
        assert root.utils.audit_trail.called
        assert root.utils.make_uuid.called
        assert customer_logic_mock.create_customer.called

    def test_create_customer_fail(self):
        # given
        requests.post = mock.MagicMock()

        root.CustomerLogic.return_error = 1

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               500))

        # when
        response = self.app.post_json('/v1/orm/customers', CUSTOMER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    @mock.patch.object(root, 'CustomerLogic')
    def test_create_flavor_duplicate_name(self, mock_customerlogic):
        my_mock = mock.MagicMock()
        my_mock.create_customer = mock.MagicMock(
            side_effect=sqlalchemy.exc.IntegrityError(
                'a', 'b',
                'Duplicate entry \'customer\' for key \'name_idx\''))
        mock_customerlogic.return_value = my_mock

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               409))

        response = self.app.post_json('/v1/orm/customers', CUSTOMER_JSON,
                                      expect_errors=True)

        self.assertEqual(response.status_int, 409)

    def test_create_flavor_duplicate_uuid(self):
        CUSTOMER_JSON['custId'] = 'test'
        create_existing_uuid = root.utils.create_existing_uuid

        root.utils.create_existing_uuid = mock.MagicMock(side_effect=TypeError('test'))

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               409))
        response = self.app.post_json('/v1/orm/customers', CUSTOMER_JSON,
                                      expect_errors=True)

        root.utils.create_existing_uuid = create_existing_uuid
        del CUSTOMER_JSON['custId']

        self.assertEqual(response.status_int, 409)

    @mock.patch.object(root, 'CustomerLogic')
    def test_create_flavor_other_error(self, mock_customerlogic):
        my_mock = mock.MagicMock()
        my_mock.create_customer = mock.MagicMock(
            side_effect=sqlalchemy.exc.IntegrityError(
                'a', 'b',
                'test \'customer\' for key \'name_idx\''))
        mock_customerlogic.return_value = my_mock

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               500))

        response = self.app.post_json('/v1/orm/customers', CUSTOMER_JSON,
                                      expect_errors=True)

        self.assertEqual(response.status_int, 500)

    def test_create_customer_fail_bad_request(self):
        # given
        requests.post = mock.MagicMock()

        root.CustomerLogic.return_error = 2

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               404))

        # when
        response = self.app.post_json('/v1/orm/customers', CUSTOMER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_update_customer(self):
        # given
        requests.put = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.put_json('/v1/orm/customers/some_id', CUSTOMER_JSON)

        # assert
        assert response.status_int == 200
        assert root.utils.audit_trail.called
        assert customer_logic_mock.update_customer.called

    def test_update_customer_fail(self):
        # given
        requests.put = mock.MagicMock()

        root.CustomerLogic.return_error = 1

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               500))

        # when
        response = self.app.put_json('/v1/orm/customers/some_id', CUSTOMER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_update_customer_fail_bad_request(self):
        # given
        requests.put = mock.MagicMock()

        root.CustomerLogic.return_error = 2

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               404))

        # when
        response = self.app.put_json('/v1/orm/customers/some_id', CUSTOMER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_get_customer(self):
        # given
        requests.get = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.get('/v1/orm/customers/some_id')

        # assert
        assert response.status_int == 200
        assert customer_logic_mock.get_customer.called

    def test_get_customer_fail_bad_request(self):
        # given
        requests.put = mock.MagicMock()

        root.CustomerLogic.return_error = 1

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               500))

        # when
        response = self.app.get('/v1/orm/customers/some_id', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        assert customer_logic_mock.get_customer.called

    def test_get_customer_fail(self):
        # given
        requests.put = mock.MagicMock()

        root.CustomerLogic.return_error = 2

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               404))

        # when
        response = self.app.get('/v1/orm/customers/some_id', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)
        assert customer_logic_mock.get_customer.called

    def test_get_list_customer(self):
        # given
        requests.get = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.get('/v1/orm/customers?region=SAN1')

        # assert
        assert customer_logic_mock.get_customer_list_by_criteria.called

    def test_get_list_customer_fail(self):
        # given
        requests.get = mock.MagicMock()
        root.CustomerLogic.return_error = 1

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               500))

        # when
        response = self.app.get('/v1/orm/customers?region=region', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_get_list_customer_bad_request(self):
        # given
        requests.get = mock.MagicMock()
        root.CustomerLogic.return_error = 2

        root.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                               500))

        # when
        response = self.app.get('/v1/orm/customers?region=region', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    @mock.patch.object(root, 'authentication')
    def test_delete_customer_success(self, mock_auth):
        response = self.app.delete('/v1/orm/customers/test')
        self.assertEqual(response.status_int, 204)

    @mock.patch.object(root, 'authentication')
    def test_delete_customer_conflict(self, mock_auth):
        root.CustomerLogic.return_error = 2
        root.err_utils.get_error = test_utils.get_error
        response = self.app.delete('/v1/orm/customers/test', expect_errors=True)

        self.assertEqual(response.status_int, 409)

    @mock.patch.object(root, 'authentication')
    def test_delete_customer_error(self, mock_auth):
        root.CustomerLogic.return_error = 1
        root.err_utils.get_error = test_utils.get_error
        response = self.app.delete('/v1/orm/customers/test', expect_errors=True)

        self.assertEqual(response.status_int, 500)


def get_mock_customer_logic():
    global customer_logic_mock
    customer_logic_mock = mock.MagicMock()

    if root.CustomerLogic.return_error == 0:
        res = Models.CustomerResultWrapper(transaction_id='1',
                                           id='1',
                                           links={},
                                           updated=None,
                                           created='1')

        list_res = Models.CustomerSummaryResponse()
        list_res.customers.append(Models.CustomerSummary(name='1', id='1', description='1'))

        customer_logic_mock.create_customer.return_value = res
        customer_logic_mock.update_customer.return_value = res
        customer_logic_mock.get_customer.return_value = Models.Customer(**RET_CUSTOMER_JSON)
        customer_logic_mock.get_customer_list_by_criteria.return_value = list_res

    elif root.CustomerLogic.return_error == 1:
        customer_logic_mock.create_customer.side_effect = SystemError()
        customer_logic_mock.update_customer.side_effect = SystemError()
        customer_logic_mock.get_customer.side_effect = SystemError()
        customer_logic_mock.delete_customer_by_uuid.side_effect = SystemError()
        customer_logic_mock.get_customer_list_by_criteria.side_effect = SystemError()

    else:
        customer_logic_mock.create_customer.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.update_customer.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.get_customer.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.delete_customer_by_uuid.side_effect = ErrorStatus(
            status_code=409)
        customer_logic_mock.get_customer_list_by_criteria.side_effect = ErrorStatus(status_code=404)

    return customer_logic_mock


class ResponseMock:
    def __init__(self, status_code=200):
        self.status_code = status_code


CUSTOMER_JSON = {
    "description": "Customer description",
    "enabled": True,
    "name": "myDomain",
    "metadata": {
        "my_server_name": "Apache1",
        "ocx_cust": "123456889"
    },
    "regions": [
        {
            "name": "SAN1",
            "type": "single",
            "quotas": [
                {
                    "compute": [
                        {
                            "instances": "10",
                            "injected-files": "10",
                            "key-pairs": "10",
                            "ram": "10"
                        }
                    ],
                    "storage": [
                        {
                            "gigabytes": "10",
                            "snapshots": "10",
                            "volumes": "10"
                        }
                    ],
                    "network": [
                        {
                            "floating-ips": "10",
                            "networks": "10",
                            "ports": "10",
                            "routers": "10",
                            "subnets": "10"
                        }
                    ]
                }
            ]
        },
        {
            "name": "AIC_MEDIUM",
            "type": "group",
            "quotas": [
                {
                    "compute": [
                        {
                            "instances": "10",
                            "injected-files": "10",
                            "key-pairs": "10",
                            "ram": "10"
                        }
                    ],
                    "storage": [
                        {
                            "gigabytes": "10",
                            "snapshots": "10",
                            "volumes": "10"
                        }
                    ],
                    "network": [
                        {
                            "floating-ips": "10",
                            "networks": "10",
                            "ports": "10",
                            "routers": "10",
                            "subnets": "10"
                        }
                    ]
                }
            ]
        }
    ],
    "users": [
        {
            "id": "userId1",
            "role": [
                "admin",
                "other"
            ]
        },
        {
            "id": "userId2",
            "role": [
                "storage"
            ]
        }
    ],
    "defaultQuotas": [
        {
            "compute": [
                {
                    "instances": "10",
                    "injected-files": "10",
                    "key-pairs": "10",
                    "ram": "10"
                }
            ],
            "storage": [
                {
                    "gigabytes": "10",
                    "snapshots": "10",
                    "volumes": "10"
                }
            ],
            "network": [
                {
                    "floating-ips": "10",
                    "networks": "10",
                    "ports": "10",
                    "routers": "10",
                    "subnets": "10"
                }
            ]
        }
    ]
}

RET_CUSTOMER_JSON = {
    "description": "Customer description",
    "enabled": True,
    "name": "myDomain",
    "metadata": {
        "my_server_name": "Apache1",
        "ocx_cust": "123456889"
    },
    "regions": [Models.Region(**{"name": "SAN1", "type": "single", "quotas": [Models.Quota(**{
        "compute": [Models.Compute(instances='1', injected_files='1', key_pairs='1', ram='1',
                                   vcpus='1', metadata_items='1', injected_file_content_bytes='1',
                                   floating_ips='1', fixed_ips='1', injected_file_path_bytes='1',
                                   server_groups='1', server_group_members='1')],
        "storage": [Models.Storage(gigabytes='1', snapshots='1', volumes='1')],
        "network": [Models.Network(floating_ips='1', networks='1', ports='1', routers='1', subnets='1',
                                   security_groups='1', security_group_rules='1', health_monitor='1',
                                   member='1', pool='1', nat_instance='1', route_table='1', vip='1')]
    })]})],
    "users": [Models.User(**
                          {"id": "userId1", "role": ["admin", "other"]})
              ],
    "defaultQuotas": [Models.Quota(**{
        "compute": [Models.Compute(instances='1', injected_files='1', key_pairs='1', ram='1',
                                   vcpus='1', metadata_items='1', injected_file_content_bytes='1',
                                   floating_ips='1', fixed_ips='1', injected_file_path_bytes='1',
                                   server_groups='1', server_group_members='1')],
        "storage": [Models.Storage(gigabytes='1', snapshots='1', volumes='1')],
        "network": [Models.Network(floating_ips='1', networks='1', ports='1', routers='1', subnets='1',
                                   security_groups='1', security_group_rules='1', health_monitor='1',
                                   member='1', pool='1', nat_instance='1', route_table='1', vip='1')]
    })]
}

INVALID_CREATE_CUSTOMER_DATA = {
    "descriptionInvalid": "Customer description",
    "enabled": True,
    "name": "myDomain",
    "metadata": {
        "my_server_name": "Apache1",
        "ocx_cust": "123456889"
    }
}
