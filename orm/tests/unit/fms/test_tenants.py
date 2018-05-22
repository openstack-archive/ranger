import requests

from orm.common.orm_common.injector import injector
from orm.services.flavor_manager.fms_rest.data.wsme import models
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus
from orm.tests.unit.fms import FunctionalTest

from mock import MagicMock

tenant_logic_mock = None

return_error = 0


class TestTenantController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('flavor_logic', get_tenant_logic_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_add_tenants(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(200, "added"))

        global return_error
        return_error = 0

        # when
        response = self.app.post_json('/v1/orm/flavors/flavor_id/tenants', TENANT_JSON)

        # assert
        assert tenant_logic_mock.add_tenants.called

    def test_add_tenants_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(('flavor_logic', get_tenant_logic_mock()))
        requests.post = MagicMock()

        # when
        response = self.app.post_json('/v1/orm/flavors/{flavor_id}/tenants/', TENANT_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_add_tenants_bad_request(self):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(('flavor_logic', get_tenant_logic_mock()))
        requests.post = MagicMock()

        # when
        response = self.app.post_json('/v1/orm/flavors/{flavor_id}/tenants/', TENANT_JSON, expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)

    def test_delete_tenant(self):
        # given
        global return_error
        return_error = 0
        injector.override_injected_dependency(('flavor_logic', get_tenant_logic_mock()))
        requests.delete = MagicMock(return_value=ResponseMock(204))

        # when
        self.app.delete('/v1/orm/flavors/flavor_id/tenants/tenant_id')

        # assert
        assert tenant_logic_mock.delete_tenant.called

    def test_delete_tenant_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(('flavor_logic', get_tenant_logic_mock()))
        requests.delete = MagicMock()

        # when
        response = self.app.delete('/v1/orm/flavors/flavor_id/tenants/{tenant_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_delete_tenant_bad_request(self):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(('flavor_logic', get_tenant_logic_mock()))
        requests.delete = MagicMock()

        # when
        response = self.app.delete('/v1/orm/flavors/flavor_id/tenants/{tenant_id}', expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)


class ResponseMock:
    def __init__(self, status_code=200, message=""):
        self.status_code = status_code
        self.message = message


def get_tenant_logic_mock():
    global tenant_logic_mock
    tenant_logic_mock = MagicMock()

    if return_error == 0:
        tenant_logic_mock.add_tenants.return_value = RET_TENANT_JSON
    elif return_error == 1:
        tenant_logic_mock.add_tenants.side_effect = SystemError()
        tenant_logic_mock.delete_tenant.side_effect = SystemError()
    else:
        tenant_logic_mock.add_tenants.side_effect = ErrorStatus(status_code=404)
        tenant_logic_mock.delete_tenant.side_effect = ErrorStatus(status_code=404)

    return tenant_logic_mock

TENANT_JSON = {
    "tenants": [
        "tenant1"
    ]
}

RET_TENANT_JSON = models.TenantWrapper(tenants=["tenant1", "tenant2"])
