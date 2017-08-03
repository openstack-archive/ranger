import requests

from cms_rest.controllers.v1.orm.customer import enabled
from cms_rest.logic.error_base import ErrorStatus
from cms_rest.model import Models
from cms_rest.tests import FunctionalTest
import mock

customer_logic_mock = None


class TestEnabledController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        enabled.authentication = mock.MagicMock()

        enabled.CustomerLogic = get_mock_customer_logic
        enabled.CustomerLogic.return_error = 0

        enabled.utils = mock.MagicMock()
        enabled.utils.make_transid.return_value = 'some_trans_id'
        enabled.utils.audit_trail.return_value = None
        enabled.utils.make_uuid.return_value = 'some_uuid'

        enabled.err_utils = mock.MagicMock()

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_enable(self):
        # given
        requests.put = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/enabled/', ENABLED_JSON)

        # assert
        self.assertTrue(response.status_int, 200)
        self.assertTrue(enabled.utils.audit_trail.called)
        self.assertTrue(customer_logic_mock.enable.called)

    def test_enable_fail(self):
        # given
        requests.put = mock.MagicMock()
        enabled.CustomerLogic.return_error = 2
        enabled.CustomerLogic = get_mock_customer_logic

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/enabled/',
                                     ENABLED_JSON, expect_errors=True)

        # assert
        self.assertTrue(response.status_int, 404)
        self.assertTrue(customer_logic_mock.enable.called)

    def test_enable_bad_request(self):
        # given
        requests.put = mock.MagicMock()
        enabled.CustomerLogic.return_error = 1
        enabled.CustomerLogic = get_mock_customer_logic

        # when
        response = self.app.put_json('/v1/orm/customers/{customer id}/enabled/',
                                     ENABLED_JSON, expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        self.assertTrue(customer_logic_mock.enable.called)


def get_mock_customer_logic():
    global customer_logic_mock
    customer_logic_mock = mock.MagicMock()

    if enabled.CustomerLogic.return_error == 0:
        res = Models.CustomerResultWrapper(transaction_id='1',
                                           id='1',
                                           links={},
                                           updated=None,
                                           created='1')

        customer_logic_mock.enable.return_value = res

    elif enabled.CustomerLogic.return_error == 1:
        customer_logic_mock.enable.side_effect = SystemError()

    elif enabled.CustomerLogic.return_error == 2:
        customer_logic_mock.enable.side_effect = ErrorStatus(status_code=404)

    return customer_logic_mock


class ResponseMock:
    def __init__(self, status_code=200):
        self.status_code = status_code


ENABLED_JSON = {
    "enabled": "true"
}
