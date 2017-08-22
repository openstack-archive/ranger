import requests

from orm.common.orm_common.injector import injector
from orm.services.flavor_manager.fms_rest.data.wsme import models
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus
from orm.tests.unit.fms import FunctionalTest

from mock import MagicMock

utils_mock = None
flavor_logic_mock = None

return_error = 0


class TestTagsController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))
        injector.override_injected_dependency(('utils', get_utils_mock()))

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_create_tags_success(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.post_json('/v1/orm/flavors/test/tags', FLAVOR_JSON)

        # assert
        self.assertEqual(response.status_int, 201)

    def test_create_tags_exception_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.post_json('/v1/orm/flavors/test/tags', FLAVOR_JSON,
                                      expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        # assert utils_mock.audit_trail.called

    def test_create_tags_errorstatus_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.post_json('/v1/orm/flavors/test/tags', FLAVOR_JSON,
                                      expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)
        # assert utils_mock.audit_trail.called

    def test_update_tags_success(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.put_json('/v1/orm/flavors/test/tags', FLAVOR_JSON)

        # assert
        self.assertEqual(response.status_int, 200)
        # assert utils_mock.audit_trail.called

    def test_update_tags_exception_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.put_json('/v1/orm/flavors/test/tags', FLAVOR_JSON,
                                     expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        # assert utils_mock.audit_trail.called

    def test_update_tags_errorstatus_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.put_json('/v1/orm/flavors/test/tags', FLAVOR_JSON,
                                     expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)
        # assert utils_mock.audit_trail.called

    def test_delete_tags_success(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.delete('/v1/orm/flavors/test/tags')

        # assert
        self.assertEqual(response.status_int, 204)
        # assert utils_mock.audit_trail.called

    def test_delete_tags_exception_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.delete('/v1/orm/flavors/test/tags',
                                   expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        # assert utils_mock.audit_trail.called

    def test_delete_tags_error_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.delete('/v1/orm/flavors/test/tags',
                                   expect_errors=True)
        # assert
        self.assertEqual(response.status_int, 500)

    def test_get_tags_success(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 0
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.get('/v1/orm/flavors/test/tags')

        # assert
        # assert response.status_int == 200

    def test_get_tags_exception_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.get('/v1/orm/flavors/test/tags',
                                expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        # assert utils_mock.audit_trail.called

    def test_get_tags_errorstatus_raised(self):
        # given
        requests.post = MagicMock(return_value=ResponseMock(201, "created"))

        global return_error
        return_error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_flavor_logic_mock()))

        # when
        response = self.app.get('/v1/orm/flavors/test/tags',
                                expect_errors=True)

        # assert
        # self.assertEqual(response.status_int, 404)


class ResponseMock:
    def __init__(self, status_code=200, message=""):
        self.status_code = status_code
        self.message = message


def get_flavor_logic_mock():
    global flavor_logic_mock
    flavor_logic_mock = MagicMock()

    if return_error == 0:
        flavor_logic_mock.get_tags.return_value = FLAVOR_JSON['tags']
        flavor_logic_mock.add_tags.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.delete_tags.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.update_tags.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.update_flavor.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.create_flavor.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.get_flavor_by_uuid.return_value = RET_FLAVOR_JSON
        flavor_logic_mock.get_flavor_by_uuid_or_name.return_value = \
            RET_FLAVOR_JSON
        flavor_logic_mock.get_flavor_list_by_params.return_value = FILTER_RET
    elif return_error == 1:
        flavor_logic_mock.get_tags.side_effect = SystemError()
        flavor_logic_mock.add_tags.side_effect = SystemError()
        flavor_logic_mock.delete_tags.side_effect = SystemError()
        flavor_logic_mock.update_tags.side_effect = SystemError()
        flavor_logic_mock.update_flavor.side_effect = SystemError()
        flavor_logic_mock.create_flavor.side_effect = SystemError()
        flavor_logic_mock.get_flavor_by_uuid.side_effect = SystemError()
        flavor_logic_mock.get_flavor_by_uuid_or_name.side_effect = \
            SystemError()
        flavor_logic_mock.get_flavor_list_by_params.side_effect = SystemError()
        flavor_logic_mock.delete_flavor_by_uuid.side_effect = SystemError()
    else:
        flavor_logic_mock.get_tags.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.add_tags.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.delete_tags.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.update_tags.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.update_flavor.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.create_flavor.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.get_flavor_by_uuid.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.get_flavor_list_by_params.side_effect = ErrorStatus(
            status_code=404)
        flavor_logic_mock.delete_flavor_by_uuid.side_effect = ErrorStatus(
            status_code=404)
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
    "tags": {
        "A": "B"
    }
}

RET_FLAVOR_JSON = models.TagsWrapper(
    FLAVOR_JSON["tags"]
)

FILTER_RET = [
    {
        "status": "Error",
        "description": "A standard 2GB Ram 2 vCPUs 50GB Disk, Flavor",
        "series": "ss",
        "extra-specs": {
            "aggregate_instance_extra_specs:ss": "true",
            "spec2": "valuespec2",
            "spec3": "valuespec3",
            "spec1": "valuespec1"
        },
        "ram": "1024",
        "ephemeral": "1",
        "visibility": "private",
        "options": {
            "option2": "valueoption2",
            "option3": "valueoption3",
            "bundle": "test",
            "option1": "valueoption1"
        },
        "regions": [
            {
                "status": "Error",
                "type": "single",
                "name": "lcp_1"
            }
        ],
        "vcpus": "20",
        "tag": {
            "tags1": "valuetags1",
            "tags2": "valuetags2",
            "tags3": "valuetags3"
        },
        "swap": "1",
        "disk": "2048",
        "tenants": [
            "070be05e-26e2-4519-a46d-224cbf8558f4",
            "4f7b9561-af8b-4cc0-87e2-319270dad49e"
        ],
        "id": "e2b86034eeec4b7abd01b9e0287a13ff",
        "name": "ss.c20r1d2048s1e1.bundleoption1option2option3"
    }]

FILTER_RET = models.FlavorListFullResponse()
FILTER_RET.flavors.append(
    models.Flavor(name='1', id='1', description='1'))
