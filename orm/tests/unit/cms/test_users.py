import mock
import requests
from wsme.exc import ClientSideError

from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer import users
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model import Models
from orm.tests.unit.cms import FunctionalTest

customer_logic_mock = None


class TestUserController(FunctionalTest):
    def setUp(self):
        global original_audit_trail
        FunctionalTest.setUp(self)

        users.authentication = mock.MagicMock()

        users.CustomerLogic = get_mock_customer_logic
        users.CustomerLogic.return_error = 0

        users.utils = mock.MagicMock()

        users.utils = mock.MagicMock()
        users.utils.make_transid.return_value = 'some_trans_id'
        users.utils.audit_trail.return_value = None
        users.utils.make_uuid.return_value = 'some_uuid'
        users.utils.make_userstransid.return_value = 'some_trans_id'

        users.err_utils = mock.MagicMock()

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_add_default_users(self):
        # given
        requests.post = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/users/', USER_JSON)

        # assert
        self.assertEqual(response.status_int, 200)
        self.assertTrue(customer_logic_mock.add_default_users.called)

    def test_add_default_users_fail(self):
        # given
        requests.post = mock.MagicMock()

        users.CustomerLogic.return_error = 1

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                500))

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/users/', USER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_add_default_users_fail_bad_request(self):
        # given
        requests.post = mock.MagicMock()

        users.CustomerLogic.return_error = 2

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                404))

        # when
        response = self.app.post_json('/v1/orm/customers/{customer id}/users/', USER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_replace_default_users(self):
        # given
        requests.put = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/users/', USER_JSON)

        # assert
        self.assertEqual(response.status_int, 200)
        self.assertTrue(customer_logic_mock.replace_default_users.called)

    def test_replace_default_users_fail(self):
        # given
        requests.put = mock.MagicMock()

        users.CustomerLogic.return_error = 1

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                500))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/users/',
                                     USER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_replace_default_users_fail_bad_request(self):
        # given
        requests.put = mock.MagicMock()

        users.CustomerLogic.return_error = 2

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                404))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/users/',
                                     USER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_delete_default_user(self):
        # given
        requests.delete = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.delete('/v1/orm/customers/{customer id}/users/{user_id}')

        # assert
        self.assertEqual(response.status_int, 204)
        self.assertTrue(users.utils.audit_trail.called)
        self.assertTrue(customer_logic_mock.delete_default_users.called)

    def test_delete_default_user_fail(self):
        # given
        requests.delete = mock.MagicMock()

        users.CustomerLogic.return_error = 1

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                500))

        # when
        response = self.app.delete('/v1/orm/customers/{customer id}/users/{user_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_delete_default_user_fail_bad_request(self):
        # given
        requests.delete = mock.MagicMock()

        users.CustomerLogic.return_error = 2

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                404))

        # when
        response = self.app.delete('/v1/orm/customers/{customer id}/users/{user_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_get_default(self):
        # given
        requests.get = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.get('/v1/orm/customers/some_id/users')

        # assert
        self.assertEqual(response.status_int, 200)

    def test_add_users(self):
        # given
        requests.post = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.post_json('/v1/orm/customers/{some_id}/regions/{some_id}/users/', USER_JSON)

        # assert
        self.assertEqual(response.status_int, 200)
        self.assertTrue(users.utils.audit_trail.called)
        self.assertTrue(customer_logic_mock.add_users.called)

    def test_add_users_fail(self):
        # given
        requests.post = mock.MagicMock()

        users.CustomerLogic.return_error = 1

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                500))

        # when
        response = self.app.post_json('/v1/orm/customers/{some_id}/regions/{some_id}/users/', USER_JSON,
                                      expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_add_users_fail_bad_request(self):
        # given
        requests.post = mock.MagicMock()

        users.CustomerLogic.return_error = 2

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                404))

        # when
        response = self.app.post_json('/v1/orm/customers/{some_id}/regions/{some_id}/users/', USER_JSON,
                                      expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_replace_users(self):
        # given
        requests.put = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.put_json('/v1/orm/customers/{some_id}/regions/{some_id}/users/', USER_JSON)

        # assert
        self.assertEqual(response.status_int, 200)
        self.assertTrue(users.utils.audit_trail.called)
        self.assertTrue(customer_logic_mock.replace_users.called)

    def test_replace_users_fail(self):
        # given
        requests.put = mock.MagicMock()

        users.CustomerLogic.return_error = 1

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                500))

        # when
        response = self.app.put_json('/v1/orm/customers/{some_id}/regions/{some_id}/users/',
                                     USER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_replace_users_fail_bad_request(self):
        # given
        requests.put = mock.MagicMock()

        users.CustomerLogic.return_error = 2

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                404))

        # when
        response = self.app.put_json('/v1/orm/customers/{some_id}/regions/{some_id}/users/',
                                     USER_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_delete_user(self):
        # given
        requests.delete = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.delete('/v1/orm/customers/{some_id}/regions/{some_id}/users/{user_id}')

        # assert
        self.assertEqual(response.status_int, 204)
        self.assertTrue(users.utils.audit_trail.called)
        self.assertTrue(customer_logic_mock.delete_users.called)

    def test_delete_user_fail(self):
        # given
        requests.delete = mock.MagicMock()

        users.CustomerLogic.return_error = 1

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                500))

        # when
        response = self.app.delete('/v1/orm/customers/{some_id}/regions/{some_id}/users/{user_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_delete_user_fail_bad_request(self):
        # given
        requests.delete = mock.MagicMock()

        users.CustomerLogic.return_error = 2

        users.err_utils.get_error = mock.MagicMock(return_value=ClientSideError("blabla",
                                                                                404))

        # when
        response = self.app.delete('/v1/orm/customers/{some_id}/regions/{some_id}/users/{user_id}', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)

    def test_get(self):
        # given
        requests.get = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.get('/v1/orm/customers/{some_id}/regions/{some_id}/users')

        # assert
        self.assertEqual(response.status_int, 200)


def get_mock_customer_logic():
    global customer_logic_mock
    customer_logic_mock = mock.MagicMock()

    if users.CustomerLogic.return_error == 0:
        res = Models.UserResultWrapper(transaction_id='1', users=[])

        customer_logic_mock.add_default_users.return_value = res
        customer_logic_mock.add_users.return_value = res
        customer_logic_mock.replace_default_users.return_value = res
        customer_logic_mock.replace_users.return_value = res

    elif users.CustomerLogic.return_error == 1:
        customer_logic_mock.add_users.side_effect = SystemError()
        customer_logic_mock.add_default_users.side_effect = SystemError()
        customer_logic_mock.replace_users.side_effect = SystemError()
        customer_logic_mock.replace_default_users.side_effect = SystemError()
        customer_logic_mock.delete_users.side_effect = SystemError()
        customer_logic_mock.delete_default_users.side_effect = SystemError()

    else:
        customer_logic_mock.add_users.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.add_default_users.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.replace_users.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.replace_default_users.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.delete_users.side_effect = ErrorStatus(status_code=404)
        customer_logic_mock.delete_default_users.side_effect = ErrorStatus(status_code=404)

    return customer_logic_mock


class ResponseMock:
    def __init__(self, status_code=200):
        self.status_code = status_code


USER_JSON = [
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
]
