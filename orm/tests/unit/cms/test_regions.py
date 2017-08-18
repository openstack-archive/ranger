import mock
import requests
from wsme.exc import ClientSideError

from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer import regions
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model import Models
from orm.tests.unit.cms import FunctionalTest

customer_logic_mock = None


class TestRegionController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        regions.authentication = mock.MagicMock()

        regions.CustomerLogic = get_mock_customer_logic
        regions.CustomerLogic.return_error = 0

        regions.utils = mock.MagicMock()
        regions.utils.make_transid.return_value = 'some_trans_id'
        regions.utils.audit_trail.return_value = None
        regions.utils.make_uuid.return_value = 'some_uuid'

        regions.err_utils = mock.MagicMock()

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_add_regions(self):
        # given
        requests.post = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/regions/', REGION_JSON)

        # assert
        assert response.status_int == 200
        assert regions.utils.audit_trail.called
        assert customer_logic_mock.add_regions.called

    def test_add_regions_fail(self):
        # given
        requests.post = mock.MagicMock()

        regions.CustomerLogic.return_error = 1

        regions.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                  500))

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/regions/', REGION_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_replace_regions_specific_region(self):
        regions.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                  405))

        response = self.app.put_json(
            '/v1/orm/customers/{customer id}/regions/test', REGION_JSON,
            expect_errors=True)
        self.assertEqual(response.status_int, 405)

    def test_add_regions_fail_bad(self):
        # given
        requests.post = mock.MagicMock()

        regions.CustomerLogic.return_error = 2

        regions.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                  404))

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/regions/', REGION_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_replace_regions(self):
        # given
        requests.put = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/regions/', REGION_JSON)

        # assert
        assert response.status_int == 200
        assert regions.utils.audit_trail.called
        assert customer_logic_mock.replace_regions.called

    def test_replace_regions_fail(self):
        # given
        requests.put = mock.MagicMock()

        regions.CustomerLogic.return_error = 1

        regions.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                  500))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/regions/', REGION_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_replace_regions_fail_bad(self):
        # given
        requests.put = mock.MagicMock()

        regions.CustomerLogic.return_error = 2

        regions.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                  404))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/regions/', REGION_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_delete_regions(self):
        # given
        requests.delete = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.delete('/v1/orm/customers/{customer id}/regions/{region_id}')

        # assert
        assert response.status_int == 204
        assert regions.utils.audit_trail.called
        assert customer_logic_mock.delete_region.called

    def test_delete_regions_fail_bad(self):
        # given
        requests.delete = mock.MagicMock()

        regions.CustomerLogic.return_error = 1

        regions.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                  500))

        # when
        response = self.app.delete('/v1/orm/customers/{customer id}/regions/{region_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_delete_regions_fail(self):
        # given
        requests.delete = mock.MagicMock()

        regions.CustomerLogic.return_error = 2

        regions.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                  404))

        # when
        response = self.app.delete('/v1/orm/customers/{customer id}/regions/{region_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_get(self):
        # given
        requests.get = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.get('/v1/orm/customers/some_id/regions/some_id')

        # assert
        assert response.status_int == 200


def get_mock_customer_logic():
    global customer_logic_mock
    customer_logic_mock = mock.MagicMock()

    if regions.CustomerLogic.return_error == 0:
        res = Models.RegionResultWrapper(transaction_id='1', regions=[])

        customer_logic_mock.add_regions.return_value = res
        customer_logic_mock.replace_regions.return_value = res

    elif regions.CustomerLogic.return_error == 1:
        customer_logic_mock.add_regions.side_effect = SystemError()
        customer_logic_mock.replace_regions.side_effect = SystemError()
        customer_logic_mock.delete_region.side_effect = SystemError()

    else:
        customer_logic_mock.add_regions.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.replace_regions.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.delete_region.side_effect = ErrorStatus(status_code=404)

    return customer_logic_mock


class ResponseMock:
    def __init__(self, status_code=200):
        self.status_code = status_code


REGION_JSON = [
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
    }
]
