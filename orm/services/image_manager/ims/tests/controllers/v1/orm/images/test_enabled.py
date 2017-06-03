import mock
import json
from ims.controllers.v1.orm.images import enabled
from ims.persistency.wsme.models import ImageWrapper

from ims.logic.error_base import ErrorStatus

from ims.tests import FunctionalTest
from wsme.exc import ClientSideError
from orm_common.injector import injector

return_error = 0


class TestGetImageDetails(FunctionalTest):
    """Main put for image activate/deactivate test case."""

    def setUp(self):
        FunctionalTest.setUp(self)
        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_enabled_put_sanity(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        response = self.app.put_json('/v1/orm/images/a/enabled/', ENABLED_JSON)

        self.assertEqual(ImageWrapper().tojson(), response.json)
        self.assertEqual(200, response.status_code)

    @mock.patch.object(enabled, 'err_utils')
    def test_enabled_put_image_not_found(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.put_json('/v1/orm/images/a/enabled/', ENABLED_JSON,
                                     expect_errors=True)

        self.assertEqual(404, response.status_code)

    @mock.patch.object(enabled, 'err_utils')
    def test_enabled_put_other_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.put_json('/v1/orm/images/a/enabled/', ENABLED_JSON,
                                     expect_errors=True)

        self.assertEqual(500, response.status_code)


def get_logic_mock():
    global image_logic_mock
    image_logic_mock = mock.MagicMock()

    if return_error == 0:
        image_logic_mock.enable_image.return_value = ImageWrapper()
    elif return_error == 1:
        image_logic_mock.enable_image.side_effect = SystemError()
    elif return_error == 2:
        image_logic_mock.enable_image.side_effect = ErrorStatus(
            status_code=404)
    elif return_error == 3:
        image_logic_mock.enable_image.side_effect = ErrorStatus(
            status_code=409)

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


def get_error(transaction_id, status_code, error_details=None,
              message=None):
    return ClientSideError(json.dumps({
        'code': status_code,
        'type': 'test',
        'created': '0.0',
        'transaction_id': transaction_id,
        'message': message if message else error_details,
        'details': 'test'
    }), status_code=status_code)


ENABLED_JSON = {
    "enabled": False
}
