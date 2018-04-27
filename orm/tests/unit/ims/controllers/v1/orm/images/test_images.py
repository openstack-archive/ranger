"""Images unittests module."""
import json

from orm.common.orm_common.injector import injector
from orm.services.image_manager.ims.controllers.v1.orm.images import images
from orm.services.image_manager.ims.logic.error_base import ErrorStatus
from orm.services.image_manager.ims.persistency.wsme.models import ImageSummaryResponse, ImageWrapper
from orm.tests.unit.ims import FunctionalTest

import mock
from wsme.exc import ClientSideError


utils_mock = None
image_logic_mock = None

return_error = 0


class TestGetImageDetails(FunctionalTest):
    """Main get_image_details test case."""

    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_get_sanity(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.get('/v1/orm/images/test')
        self.assertEqual(ImageWrapper().tojson(), response.json)

    @mock.patch.object(images, 'err_utils')
    def test_get_image_not_found(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.get('/v1/orm/images/test', expect_errors=True)
        self.assertEqual(404, response.status_code)

    @mock.patch.object(images, 'err_utils')
    def test_get_image_other_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.get('/v1/orm/images/test', expect_errors=True)
        self.assertEqual(500, response.status_int)


class TestDeleteImage(FunctionalTest):
    """main test delete image."""

    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_delete_success(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.delete('/v1/orm/images/test')
        self.assertEqual(response.status_int, 204)

    @mock.patch.object(images, 'err_utils')
    def test_delete_not_found_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.delete('/v1/orm/images/test', expect_errors=True)
        self.assertEqual(response.status_int, 404)

    @mock.patch.object(images, 'err_utils')
    def test_delete_general_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.delete('/v1/orm/images/test', expect_errors=True)
        self.assertEqual(response.status_int, 500)


class TestUpdateImage(FunctionalTest):
    """test update image."""

    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_update_image_success(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        response = self.app.put_json('/v1/orm/images/updatetest', image_json)

        self.assertEqual(ImageWrapper().tojson(), response.json)
        self.assertEqual(200, response.status_code)

    @mock.patch.object(images, 'err_utils')
    def test_update_image_NotFound(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.put_json('/v1/orm/images/updatetest', image_json,
                                     expect_errors=True)

        self.assertEqual(404, response.status_code)

    @mock.patch.object(images, 'err_utils')
    def test_update_image_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.put_json('/v1/orm/images/updatetest', image_json,
                                     expect_errors=True)
        self.assertEqual(500, response.status_code)


class TestListImage(FunctionalTest):
    """main test delete image."""

    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_list_success(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.get('/v1/orm/images/?region=SAN1')

        self.assertEqual(ImageSummaryResponse().tojson(), response.json)
        self.assertEqual(response.status_int, 200)

    @mock.patch.object(images, 'err_utils')
    def test_list_not_found_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 2
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.get('/v1/orm/images/?region=rd', expect_errors=True)

        self.assertEqual(404, response.status_int)

    @mock.patch.object(images, 'err_utils')
    def test_list_general_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.get('/v1/orm/images/?region=SAN1', expect_errors=True)

        self.assertEqual(500, response.status_int)


class TestCreateImage(FunctionalTest):
    """Main create_image test case."""

    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(('image_logic', get_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_create_sanity(self):
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.post_json('/v1/orm/images', image_json)
        self.assertEqual(ImageWrapper().tojson(), response.json)
        self.assertEqual(201, response.status_int)

    def test_create_with_id(self):
        image_json["image"].update({"id": "test"})
        global return_error
        return_error = 0
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.post_json('/v1/orm/images', image_json)
        self.assertEqual(ImageWrapper().tojson(), response.json)
        del image_json['image']['id']
        self.assertEqual(201, response.status_int)

    @mock.patch.object(images, 'err_utils')
    def test_create_errorstatus_raised(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 3
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.post_json('/v1/orm/images', image_json,
                                      expect_errors=True)

        self.assertEqual(409, response.status_int)

    @mock.patch.object(images, 'err_utils')
    def test_create_other_error(self, mock_err_utils):
        mock_err_utils.get_error = get_error

        global return_error
        return_error = 1
        injector.override_injected_dependency(('image_logic', get_logic_mock()))

        response = self.app.post_json('/v1/orm/images', image_json,
                                      expect_errors=True)

        self.assertEqual(500, response.status_int)


def get_logic_mock():
    global image_logic_mock
    image_logic_mock = mock.MagicMock()

    if return_error == 0:
        image_logic_mock.update_image.return_value = ImageWrapper()
        image_logic_mock.create_image.return_value = ImageWrapper()
        image_logic_mock.get_image_by_uuid.return_value = ImageWrapper()
        image_logic_mock.get_image_list_by_params.return_value = ImageSummaryResponse()
    elif return_error == 1:
        image_logic_mock.update_image.side_effect = SystemError()
        image_logic_mock.create_image.side_effect = SystemError()
        image_logic_mock.get_image_by_uuid.side_effect = SystemError()
        image_logic_mock.get_image_list_by_params.side_effect = SystemError()
        image_logic_mock.delete_image_by_uuid.side_effect = SystemError()
    elif return_error == 2:
        image_logic_mock.update_image.side_effect = ErrorStatus(
            status_code=404)
        image_logic_mock.create_image.side_effect = ErrorStatus(
            status_code=404)
        image_logic_mock.get_image_by_uuid.side_effect = ErrorStatus(
            status_code=404)
        image_logic_mock.get_image_list_by_params.side_effect = ErrorStatus(
            status_code=404)
        image_logic_mock.delete_image_by_uuid.side_effect = ErrorStatus(
            status_code=404)
    elif return_error == 3:
        image_logic_mock.create_image.side_effect = ErrorStatus(
            status_code=409)
        image_logic_mock.update_image.side_effect = ErrorStatus(
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


image_json = \
    {
        "image":
        {
            "name": "abcde1e236",
            "url": "https://mirrors.it.att.com/images/image-name",
            "visibility": "private",
            "disk-format": "raw",
            "container-format": "bare",
            "min-disk": 1,
            "min-ram": 1,
            "tags": ["tag"],
            "properties": {
                "property1": "value1"
            },
            "regions": [{
                "name": "rdm1",
                "type": "single"
            }],
            "customers": [
                "da3b75d9-3f4a-40e7-8a2c-bfab23927dea"
            ]
        }
    }
