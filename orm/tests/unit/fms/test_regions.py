import requests

from orm.common.orm_common.injector import injector
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors import regions
from orm.services.flavor_manager.fms_rest.data.wsme import models
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus
from orm.tests.unit.fms import FunctionalTest
from orm.tests.unit.fms import test_utils

from mock import MagicMock, patch

utils_mock = None
region_logic_mock = None

return_error = 0


class TestRegionController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('flavor_logic', get_region_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_add_regions(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(200, "added"))

        global return_error
        return_error = 0

        # when
        response = self.app.post_json('/v1/orm/flavors/flavor_id/regions', REGION_JSON)

        # assert
        assert utils_mock.audit_trail.called
        assert region_logic_mock.add_regions.called

    def test_add_regions_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(('flavor_logic', get_region_logic_mock()))
        requests.post = MagicMock()

        # when
        response = self.app.post_json('/v1/orm/flavors/{flavor_id}/regions/', REGION_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    @patch.object(regions, 'err_utils')
    def test_add_regions_bad_request(self, mock_err_utils):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(('flavor_logic', get_region_logic_mock()))
        requests.post = MagicMock()
        mock_err_utils.get_error = test_utils.get_error

        # when
        response = self.app.post_json('/v1/orm/flavors/{flavor_id}/regions/', REGION_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_delete_region(self):
        # given
        global return_error
        return_error = 0
        injector.override_injected_dependency(('flavor_logic', get_region_logic_mock()))
        requests.delete = MagicMock(return_value=ResponseMock(204))

        # when
        self.app.delete('/v1/orm/flavors/flavor_id/regions/region_id')

        # assert
        assert utils_mock.audit_trail.called
        assert region_logic_mock.delete_region.called

    def test_delete_region_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(('flavor_logic', get_region_logic_mock()))
        requests.delete = MagicMock()

        # when
        response = self.app.delete('/v1/orm/flavors/flavor_id/regions/{region_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_delete_region_bad_request(self):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(('flavor_logic', get_region_logic_mock()))
        requests.delete = MagicMock()

        # when
        response = self.app.delete('/v1/orm/flavors/flavor_id/regions/{region_id}', expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)


class ResponseMock:
    def __init__(self, status_code=200, message=""):
        self.status_code = status_code
        self.message = message


def get_region_logic_mock():
    global region_logic_mock
    region_logic_mock = MagicMock()

    if return_error == 0:
        region_logic_mock.add_regions.return_value = RET_REGION_JSON
    elif return_error == 1:
        region_logic_mock.add_regions.side_effect = SystemError()
        region_logic_mock.delete_region.side_effect = SystemError()
    else:
        region_logic_mock.add_regions.side_effect = ErrorStatus(status_code=404)
        region_logic_mock.delete_region.side_effect = ErrorStatus(status_code=404)

    return region_logic_mock


def get_utils_mock():
    global utils_mock
    utils_mock = MagicMock()

    utils_mock.make_transid.return_value = 'some_trans_id'
    utils_mock.audit_trail.return_value = None
    utils_mock.make_uuid.return_value = 'some_uuid'

    return utils_mock


REGION_JSON = {
    "regions": [
        {"name": "76", "type": "single"}
    ]
}

RET_REGION_JSON = models.RegionWrapper([models.Region(name='76', status='done')])
