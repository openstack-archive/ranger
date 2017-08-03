import requests

from cms_rest.controllers.v1.orm.customer import metadata
from cms_rest.logic.error_base import ErrorStatus
from cms_rest.model import Models
from cms_rest.tests import FunctionalTest
import mock

metadata_logic_mock = None


class TestMetadataController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        metadata.authentication = mock.MagicMock()

        metadata.logic.return_error = 0
        metadata.logic = get_mock_customer_logic()

        metadata.utils = mock.MagicMock()
        metadata.utils.make_transid.return_value = 'some_trans_id'
        metadata.utils.audit_trail.return_value = None
        metadata.utils.make_uuid.return_value = 'some_uuid'

        metadata.err_utils = mock.MagicMock()

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_add_metadata(self):
        # given
        requests.post = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/metadata/', METADATA_JSON)

        # assert
        self.assertTrue(response.status_int, 200)
        self.assertTrue(metadata.utils.audit_trail.called)
        self.assertTrue(metadata_logic_mock.add_customer_metadata.called)

    def test_add_metadata_fail(self):
        # given
        requests.post = mock.MagicMock()
        metadata.logic.return_error = 2
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/metadata/',
                                      METADATA_JSON, expect_errors=True)

        # assert
        self.assertTrue(response.status_int, 404)
        self.assertTrue(metadata_logic_mock.add_customer_metadata.called)

    def test_add_metadata_bad_request(self):
        # given
        requests.post = mock.MagicMock()
        metadata.logic.return_error = 1
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/metadata/',
                                      METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.add_customer_metadata.called)

    def test_add_metadata_lu_Error(self):
        # given
        requests.post = mock.MagicMock()
        metadata.logic.return_error = 3
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/metadata/',
                                      METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.add_customer_metadata.called)

    def test_add_metadata_att_Error(self):
        # given
        requests.post = mock.MagicMock()
        metadata.logic.return_error = 4
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/metadata/',
                                      METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.add_customer_metadata.called)

    def test_add_metadata_value_Error(self):
        # given
        requests.post = mock.MagicMock()
        metadata.logic.return_error = 5
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/metadata/',
                                      METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.add_customer_metadata.called)

    def test_update_metadata(self):
        # given
        requests.put = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/metadata/', METADATA_JSON)

        # assert
        self.assertTrue(response.status_int, 200)
        self.assertTrue(metadata.utils.audit_trail.called)
        self.assertTrue(metadata_logic_mock.update_customer_metadata.called)

    def test_update_metadata_fail(self):
        # given
        requests.put = mock.MagicMock()
        metadata.logic.return_error = 2
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/metadata/',
                                     METADATA_JSON, expect_errors=True)

        # assert
        self.assertTrue(response.status_int, 404)
        self.assertTrue(metadata_logic_mock.update_customer_metadata.called)

    def test_update_metadata_bad_request(self):
        # given
        requests.put = mock.MagicMock()
        metadata.logic.return_error = 1
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/metadata/',
                                     METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.update_customer_metadata.called)

    def test_update_metadata_lu_Error(self):
        # given
        requests.put = mock.MagicMock()
        metadata.logic.return_error = 3
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/metadata/',
                                     METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.update_customer_metadata.called)

    def test_update_metadata_att_Error(self):
        # given
        requests.put = mock.MagicMock()
        metadata.logic.return_error = 4
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/metadata/',
                                     METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.update_customer_metadata.called)

    def test_update_metadata_value_Error(self):
        # given
        requests.put = mock.MagicMock()
        metadata.logic.return_error = 5
        metadata.logic = get_mock_customer_logic()

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/metadata/',
                                     METADATA_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(metadata_logic_mock.update_customer_metadata.called)


def get_mock_customer_logic():
    global metadata_logic_mock
    metadata_logic_mock = mock.MagicMock()

    if metadata.logic.return_error == 0:
        res = Models.CustomerResultWrapper(transaction_id='1',
                                           id='1',
                                           links={},
                                           updated=None,
                                           created='1')

        metadata_logic_mock.add_customer_metadata.return_value = res
        metadata_logic_mock.update_customer_metadata.return_value = res

    elif metadata.logic.return_error == 1:
        metadata_logic_mock.add_customer_metadata.side_effect = SystemError()
        metadata_logic_mock.update_customer_metadata.side_effect = SystemError()

    elif metadata.logic.return_error == 2:
        metadata_logic_mock.add_customer_metadata.side_effect = ErrorStatus(status_code=404)
        metadata_logic_mock.update_customer_metadata.side_effect = ErrorStatus(status_code=404)

    elif metadata.logic.return_error == 3:
        metadata_logic_mock.add_customer_metadata.side_effect = LookupError()
        metadata_logic_mock.update_customer_metadata.side_effect = LookupError()

    elif metadata.logic.return_error == 4:
        metadata_logic_mock.add_customer_metadata.side_effect = AttributeError()
        metadata_logic_mock.update_customer_metadata.side_effect = AttributeError()

    elif metadata.logic.return_error == 5:
        metadata_logic_mock.add_customer_metadata.side_effect = ValueError()
        metadata_logic_mock.update_customer_metadata.side_effect = ValueError()

    return metadata_logic_mock


class ResponseMock:
    def __init__(self, status_code=200):
        self.status_code = status_code


METADATA_JSON = {
    "metadata": {
        "my_server_name": "Apache1",
        "ocx_cust": "12356889"
    }
}
