import copy
import requests

from orm.common.orm_common.injector import injector
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors import flavors
from orm.services.flavor_manager.fms_rest.data.wsme import models
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus
from orm.tests.unit.fms import FunctionalTest
from orm.tests.unit.fms import test_utils

from mock import MagicMock, patch

utils_mock = None
flavor_logic_mock = None

return_error = 0


class TestFlavorController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_create_flavor(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 0

        # when
        response = self.app.post_json('/v1/orm/flavors', FLAVOR_JSON)

        # assert
        assert response.status_int == 201
        assert utils_mock.audit_trail.called
        assert flavor_logic_mock.create_flavor.called

    def test_create_flavor_predefined_id(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))
        test_json = copy.deepcopy(FLAVOR_JSON)
        test_json['flavor']['id'] = 'test'
        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

        # when
        response = self.app.post_json('/v1/orm/flavors', test_json)

        # assert
        self.assertEqual(response.status_int, 201)

    def test_create_flavor_existing_predefined_id(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))
        test_json = copy.deepcopy(FLAVOR_JSON)
        test_json['flavor']['id'] = 'test'
        global return_error
        return_error = 1
        injector.override_injected_dependency(('utils', get_utils_mock()))

        # when
        response = self.app.post_json('/v1/orm/flavors', test_json,
                                      expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 409)

    def test_create_flavor_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.post = MagicMock(return_value=ResponseMock(400, "failed"))

        # when
        response = self.app.post_json('/v1/orm/flavors', FLAVOR_JSON,
                                      expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 409)

# Following tests not providing consistent results
#    @patch.object(flavors, 'di')
#    def test_create_flavor_duplicate_entry(self, mock_di):
#        my_mock = MagicMock()
#        my_mock.create_flavor = MagicMock(
#            side_effect=sqlalchemy.exc.IntegrityError(
#                'a', 'b',
#                'Duplicate entry \'flavor\' for key \'name_idx\''))
#        mock_di.resolver.unpack = MagicMock(
#            return_value=(my_mock, MagicMock(),))
#
#        response = self.app.post_json('/v1/orm/flavors', FLAVOR_JSON,
#                                      expect_errors=True)
#
#        self.assertEqual(response.status_int, 409)
#
#    @patch.object(flavors, 'di')
#    def test_create_flavor_other_error(self, mock_di):
#        my_mock = MagicMock()
#        my_mock.create_flavor = MagicMock(
#            side_effect=sqlalchemy.exc.IntegrityError(
#                'a', 'b',
#                'test \'flavor\' for key \'name_idx\''))
#        mock_di.resolver.unpack = MagicMock(
#            return_value=(my_mock, MagicMock(),))
#
#        response = self.app.post_json('/v1/orm/flavors', FLAVOR_JSON,
#                                      expect_errors=True)
#
#        self.assertEqual(response.status_int, 409)

    @patch.object(flavors, 'err_utils')
    def test_create_flavor_bad_request(self, mock_err_utils):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.post = MagicMock(return_value=ResponseMock(400, "failed"))
        mock_err_utils.get_error = test_utils.get_error

        # when
        response = self.app.post_json('/v1/orm/flavors', FLAVOR_JSON,
                                      expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 409)

    def test_update_flavor(self):
        # given

        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.put = MagicMock()

        # when
        response = self.app.put_json('/v1/orm/flavors/some_id', FLAVOR_JSON,
                                     expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 405)

    def test_get_flavor(self):
        # given

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock(return_value=ResponseMock(200, "updated"))

        # when
        response = self.app.get('/v1/orm/flavors/some_id')

        # assert
        assert flavor_logic_mock.get_flavor_by_uuid_or_name.called

    def test_get_flavor_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock()

        # when
        response = self.app.get('/v1/orm/flavors/some_id', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_get_flavor_bad_request(self):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock()

        # when
        response = self.app.get('/v1/orm/flavors/some_id', expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)

    # 8/8/16 Bug DE226006 - This bug fix is to return 405 for every attempt
    # to delete flavor.
    def test_delete_flavor(self):
        # given
        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.delete = MagicMock()

        # when
        response = self.app.delete('/v1/orm/flavors/some_id',
                                   expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 204)

    def test_delete_flavor_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.delete = MagicMock()

        # when
        response = self.app.delete('/v1/orm/flavors/some_id',
                                   expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    @patch.object(flavors, 'err_utils')
    def test_delete_flavor_bad_request(self, mock_err_utils):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.delete = MagicMock()
        mock_err_utils.get_error = test_utils.get_error

        # when
        response = self.app.delete('/v1/orm/flavors/some_id',
                                   expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 409)

    def test_get_all_flavor(self):
        # given

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock(return_value=ResponseMock(200, "updated"))

        # when
        response = self.app.get('/v1/orm/flavors?region=SAN1')

        # assert
        assert flavor_logic_mock.get_flavor_list_by_params.called

    def test_get_all_flavor_fail(self):
        # given
        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock()

        # when
        response = self.app.get('/v1/orm/flavors?region=region',
                                expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_get_by_vm_type(self):
        # given

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock(return_value=ResponseMock(200, "updated"))

        # when
        response = self.app.get('/v1/orm/flavors?vm_type=TEST_VM_TYPE')

        # assert
        assert flavor_logic_mock.get_flavor_list_by_params.called

    def test_get_by_vnf_name(self):
        # given

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock(return_value=ResponseMock(200, "updated"))

        # when
        response = self.app.get('/v1/orm/flavors?vnf_name=TEST_VNF_NAME')

        # assert
        assert flavor_logic_mock.get_flavor_list_by_params.called

    def test_get_all_flavor_bad_request(self):
        # given
        global return_error
        return_error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        requests.get = MagicMock()

        # when
        response = self.app.get('/v1/orm/flavors?region=region',
                                expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)


class ResponseMock:
    def __init__(self, status_code=200, message=""):
        self.status_code = status_code
        self.message = message

    def json(self):
        return {'uuid': 'test'}


def get_flavor_logic_mock():
    global flavor_logic_mock
    flavor_logic_mock = MagicMock()

    if return_error == 0:
        flavor_logic_mock.update_flavor.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.create_flavor.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.get_flavor_by_uuid.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.get_flavor_by_uuid_or_name.return_value = \
            RET_FLAVOR_JSON
        flavor_logic_mock.get_flavor_list_by_params.return_value = FILTER_RET
    elif return_error == 1:
        flavor_logic_mock.update_flavor.side_effect = SystemError()
        flavor_logic_mock.create_flavor.side_effect = SystemError()
        flavor_logic_mock.get_flavor_by_uuid.side_effect = SystemError()
        flavor_logic_mock.get_flavor_by_uuid_or_name.side_effect = \
            SystemError()
        flavor_logic_mock.get_flavor_list_by_params.side_effect = SystemError()
        flavor_logic_mock.delete_flavor_by_uuid.side_effect = SystemError()
    else:
        flavor_logic_mock.update_flavor.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.create_flavor.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.get_flavor_by_uuid.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.get_flavor_list_by_params.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.delete_flavor_by_uuid.side_effect = ErrorStatus(
            status_code=409)
        flavor_logic_mock.get_flavor_by_uuid_or_name.side_effect = ErrorStatus(
            status_code=404)

    return flavor_logic_mock


def get_utils_mock():
    global utils_mock
    utils_mock = MagicMock()

    utils_mock.make_transid.return_value = 'some_trans_id'
    utils_mock.audit_trail.return_value = None
    utils_mock.make_uuid.return_value = 'some_uuid'

    if return_error:
        utils_mock.create_existing_uuid.side_effect = TypeError('test')
    else:
        utils_mock.create_existing_uuid.return_value = 'some_uuid'

    return utils_mock


FLAVOR_JSON = {
    "flavor": {
        "description": "A standard 2GB Ram 2 vCPUs 50GB Disk, Flavor",
        "series": "nv",
        "ram": "05",
        "vcpus": "2",
        "disk": "50",
        "swap": "1024",
        "ephemeral": "0",
        "extra-specs": {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        },
        "options": {
            "option2": "valueoption2",
            "option3": "valueoption3",
            "option1": "valueoption1"
        },
        "tag": {
            "tags1": "valuetags1",
            "tags2": "valuetags2",
            "tags3": "valuetags3"
        },
        "regions": [
            {"name": "0", "type": "single"},
            {"name": "1", "type": "single"}
        ],
        "visibility": "private",
        "tenants": [
            "4f7b9561-af8b-4cc0-87e2-319270dad49e",
            "070be05e-26e2-4519-a46d-224cbf8558f4"
        ],
        "status": "complete"
    }
}

RET_FLAVOR_JSON = models.FlavorWrapper(
    models.Flavor(
        description="A standard 2GB Ram 2 vCPUs 50GB Disk, Flavor",
        series="nv",
        ram="05",
        vcpus="2",
        disk="50",
        swap="1024",
        ephemeral="0",
        extra_specs={
            "key1": "value1"
        },
        tag={
            "tags1": "valuetags1"
        },
        options={
            "option1": "valueoption1"
        },
        regions=[models.Region(name='1')],
        visibility="private",
        tenants=[
            "4f7b9561-af8b-4cc0-87e2-319270dad49e",
            "070be05e-26e2-4519-a46d-224cbf8558f4"
        ],
        status="complete"
    )
)

# FILTER_RET = [models.Flavor()]

FILTER_RET = models.FlavorListFullResponse()
FILTER_RET.flavors.append(
    models.Flavor(name='1', id='1', description='1'))
