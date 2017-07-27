import mock
import json
from wsme.exc import ClientSideError
from ims.tests import FunctionalTest

from ims.controllers.v1.orm.images import metadata


metadata_input = {
    "metadata": {
        "checksum": "1",
        "virtual_size": "@",
        "size": "3"
    }
}


class TestMetaDataController(FunctionalTest):
    """metadata controller(api) unittests."""

    @staticmethod
    def get_error(transaction_id, status_code, error_details=None,
                  message=None):
        return ClientSideError(json.dumps(
            {'code': status_code, 'type': 'test', 'created': '0.0',
             'transaction_id': transaction_id,
             'message': message if message else error_details,
             'details': 'test'}), status_code=status_code)

    def setUp(self):
        FunctionalTest.setUp(self)

    def tearDown(self):
        FunctionalTest.tearDown(self)

    @mock.patch.object(metadata, 'di')
    def test_post_metadata_success(self, mock_di):
        mock_di.resolver.unpack.return_value = get_mocks()
        response = self.app.post_json(
            '/v1/orm/images/image_id/regions/region_name/metadata',
            metadata_input)
        self.assertEqual(200, response.status_code)

    @mock.patch.object(metadata, 'err_utils')
    @mock.patch.object(metadata, 'di')
    def test_post_metadata_not_found(self, mock_di, mock_error_utils):
        mock_error_utils.get_error = self.get_error
        mock_di.resolver.unpack.return_value = get_mocks(error=404)
        response = self.app.post_json(
            '/v1/orm/images/image_id/regions/region_name/metadata',
            metadata_input, expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         'not found')

    @mock.patch.object(metadata, 'err_utils')
    @mock.patch.object(metadata, 'di')
    def test_post_metadata_error(self, mock_di, mock_error_utils):
        mock_error_utils.get_error = self.get_error
        mock_di.resolver.unpack.return_value = get_mocks(error=500)
        response = self.app.post_json(
            '/v1/orm/images/image_id/regions/region_name/metadata',
            metadata_input, expect_errors=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         'unknown error')


def get_mocks(error=None):

    metadata_logic = mock.MagicMock()
    utils = mock.MagicMock()
    metadata_logic.add_metadata.return_value = mock.MagicMock()
    if error:
        metadata_logic.add_metadata.side_effect = {404: metadata.ErrorStatus(error, 'not found'),
                                                   500: Exception("unknown error")}[error]
    return metadata_logic, utils
