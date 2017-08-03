import json

from ims.controllers.v1.orm.images import regions
from ims.logic.error_base import ErrorStatus
from ims.persistency.wsme.models import RegionWrapper
from ims.tests import FunctionalTest
import mock
from orm_common.injector import injector
from wsme.exc import ClientSideError

utils_mock = None
image_logic_mock = None

return_error = 0


class TestRegionController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_add_regions_sanity(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        response = self.app.post_json('/v1/orm/images/id/regions', REGIONS)
        self.assertEqual(RegionWrapper().tojson(), response.json)
        self.assertEqual(201, response.status_int)

    @mock.patch.object(regions, 'err_utils')
    def test_add_regions_errorstatus_raised(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.post_json('/v1/orm/images/id/regions', REGIONS,
                                      expect_errors=True)

        self.assertEqual(404, response.status_int)

    @mock.patch.object(regions, 'err_utils')
    def test_add_regions_other_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.post_json('/v1/orm/images/id/regions', REGIONS,
                                      expect_errors=True)

        self.assertEqual(500, response.status_int)

    def test_update_regions_success(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        response = self.app.put_json('/v1/orm/images/id/regions', REGIONS)

        self.assertEqual(RegionWrapper().tojson(), response.json)
        self.assertEqual(200, response.status_code)

    @mock.patch.object(regions, 'err_utils')
    def test_update_regions_NotFound(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.put_json('/v1/orm/images/id/regions', REGIONS,
                                     expect_errors=True)

        self.assertEqual(404, response.status_code)

    @mock.patch.object(regions, 'err_utils')
    def test_update_regions_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.put_json('/v1/orm/images/id/regions', REGIONS,
                                     expect_errors=True)
        self.assertEqual(500, response.status_code)

    def test_delete_success(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.delete('/v1/orm/images/id/regions/1')
        self.assertEqual(response.status_int, 204)

    @mock.patch.object(regions, 'err_utils')
    def test_delete_not_found_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.delete('/v1/orm/images/id/regions/1',
                                   expect_errors=True)
        self.assertEqual(response.status_int, 404)

    @mock.patch.object(regions, 'err_utils')
    def test_delete_general_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.delete('/v1/orm/images/id/regions/1',
                                   expect_errors=True)
        self.assertEqual(response.status_int, 500)


class ResponseMock:
    def __init__(self, status_code=200, message=""):
        self.status_code = status_code
        self.message = message


def get_logic_mock():
    global image_logic_mock
    image_logic_mock = mock.MagicMock()

    if return_error == 0:
        image_logic_mock.add_regions.return_value = RegionWrapper()
        image_logic_mock.replace_regions.return_value = RegionWrapper()
    elif return_error == 1:
        image_logic_mock.add_regions.side_effect = SystemError()
        image_logic_mock.replace_regions.side_effect = SystemError()
        image_logic_mock.delete_region.side_effect = SystemError()
    elif return_error == 2:
        image_logic_mock.add_regions.side_effect = ErrorStatus(status_code=404)
        image_logic_mock.replace_regions.side_effect = ErrorStatus(status_code=404)
        image_logic_mock.delete_region.side_effect = ErrorStatus(status_code=404)

    return image_logic_mock


def get_utils_mock():
    global utils_mock
    utils_mock = mock.MagicMock()

    utils_mock.make_transid.return_value = 'some_trans_id'
    utils_mock.audit_trail.return_value = None
    utils_mock.make_uuid.return_value = 'some_uuid'

    if return_error:
        utils_mock.create_existing_uuid.side_effect = TypeError('test')
    else:
        utils_mock.create_existing_uuid.return_value = 'some_uuid'

    return utils_mock


def get_error(transaction_id, status_code, error_details=None, message=None):
    return ClientSideError(json.dumps({
        'code': status_code,
        'type': 'test',
        'created': '0.0',
        'transaction_id': transaction_id,
        'message': message if message else error_details,
        'details': 'test'
    }), status_code=status_code)


REGIONS = {
    "regions": [
        {
            "name": "rdm1",
            "type": "single"
        }
    ]
}
