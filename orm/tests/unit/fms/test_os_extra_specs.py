from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors import os_extra_specs as es
from orm.services.flavor_manager.fms_rest.data.wsme import models
from orm.services.flavor_manager.fms_rest.logic.error_base import NotFoundError
from orm.tests.unit.fms import FunctionalTest

from mock import MagicMock, patch


class TestOsExtraSpecsController(FunctionalTest):
    """unittes."""

    @patch.object(es, 'di')
    def test_create_os_flavor_specs_success(self, mock_di):
        mock_di.resolver.unpack.return_value =\
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        response = self.app.post_json('/v1/orm/flavors/123/os_extra_specs',
                                      flavor_extra_specs_json)
        self.assertEqual(response.json, flavor_extra_specs_json)
        self.assertEqual(response.status_code, 201)

    # def test_create_os_extra_specs_bad_json(self):
    #     global flavor_extra_specs_json
    #     backup = dict(flavor_extra_specs_json)
    #     del(flavor_extra_specs_json["os_extra_specs"])
    #     response = self.app.post_json('/v1/orm/flavors/123/os_extra_specs',
    #                                   flavor_extra_specs_json,
    #                                   expect_errors=True)
    #     flavor_extra_specs_json = backup
    #     self.assertEqual(response.status_code, 400)

    @patch.object(es, 'di')
    def test_create_os_flavor_specs_audit_trial_fails(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        utils_mock.audit_trail.side_effect = SystemError()
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.post_json('/v1/orm/flavors/123/os_extra_specs',
                                      flavor_extra_specs_json,
                                      expect_errors=True)
        self.assertEqual(response.status_code, 500)

    @patch.object(es, 'di')
    def test_create_os_flavor_specs_flavor_not_found(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        flavor_mock.add_extra_specs.side_effect = NotFoundError(404,
                                                                "not found")
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.post_json('/v1/orm/flavors/123/os_extra_specs',
                                      flavor_extra_specs_json,
                                      expect_errors=True)

        # dict_body = json.loads(response.body)
        # my_json = json.loads(dict_body['faultstring'])

        # self.assertEqual(response.status_code, 404)
        # self.assertEqual(my_json['message'], 'not found')

    @patch.object(es, 'di')
    def test_update_os_flavor_specs_success(self, mock_di):
        mock_di.resolver.unpack.return_value = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        response = self.app.put_json('/v1/orm/flavors/123/os_extra_specs',
                                     flavor_extra_specs_json)
        self.assertEqual(response.json, flavor_extra_specs_json)
        self.assertEqual(response.status_code, 200)

    # def test_update_os_extra_specs_bad_json(self):
    #     global flavor_extra_specs_json
    #     backup = dict(flavor_extra_specs_json)
    #     del (flavor_extra_specs_json["os_extra_specs"])
    #     response = self.app.put_json('/v1/orm/flavors/123/os_extra_specs',
    #                                  flavor_extra_specs_json,
    #                                  expect_errors=True)
    #     flavor_extra_specs_json = backup
    #     self.assertEqual(response.status_code, 400)

    @patch.object(es, 'di')
    def test_update_os_flavor_specs_audit_trial_fails(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        utils_mock.audit_trail.side_effect = SystemError()
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.put_json('/v1/orm/flavors/123/os_extra_specs',
                                     flavor_extra_specs_json,
                                     expect_errors=True)
        self.assertEqual(response.status_code, 500)

    @patch.object(es, 'di')
    def test_update_os_flavor_specs_flavor_not_found(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        flavor_mock.update_extra_specs.side_effect = NotFoundError(404,
                                                                   "not found")
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.put_json('/v1/orm/flavors/123/os_extra_specs',
                                     flavor_extra_specs_json,
                                     expect_errors=True)

        # dict_body = json.loads(response.body)
        # my_json = json.loads(dict_body['faultstring'])

        # self.assertEqual(response.status_code, 404)
        # self.assertEqual(my_json['message'], 'not found')

    @patch.object(es, 'di')
    def test_get_os_flavor_specs_flavor_not_found(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        flavor_mock.get_extra_specs_uuid.side_effect = NotFoundError(404,
                                                                     "not found")
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.get('/v1/orm/flavors/123/os_extra_specs',
                                expect_errors=True)

        # dict_body = json.loads(response.body)
        # my_json = json.loads(dict_body['faultstring'])

        # self.assertEqual(response.status_code, 404)
        # self.assertEqual(my_json['message'], 'not found')

    @patch.object(es, 'di')
    def test_get_os_flavor_specs_success(self, mock_di):
        mock_di.resolver.unpack.return_value = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        response = self.app.get('/v1/orm/flavors/123/os_extra_specs')
        self.assertEqual(response.json, flavor_extra_specs_json)
        self.assertEqual(response.status_code, 200)

    @patch.object(es, 'di')
    def test_get_os_flavor_specs_audit_trial_fails(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        utils_mock.audit_trail.side_effect = SystemError()
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.get('/v1/orm/flavors/123/os_extra_specs',
                                expect_errors=True)
        self.assertEqual(response.status_code, 500)

    @patch.object(es, 'di')
    def test_delete_os_flavor_specs_success(self, mock_di):
        mock_di.resolver.unpack.return_value = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        response = self.app.delete('/v1/orm/flavors/123/os_extra_specs')
        self.assertEqual(response.status_code, 204)

    @patch.object(es, 'di')
    def test_delete_os_flavor_specs_audit_trial_fails(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        utils_mock.audit_trail.side_effect = SystemError()
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.delete('/v1/orm/flavors/123/os_extra_specs',
                                   flavor_extra_specs_json,
                                   expect_errors=True)
        self.assertEqual(response.status_code, 500)

    @patch.object(es, 'di')
    def test_delete_os_flavor_specs_flavor_not_found(self, mock_di):
        flavor_mock, utils_mock = \
            get_utils_flavor_logic_mock(flavor_extra_specs_json)
        flavor_mock.delete_extra_specs.side_effect = NotFoundError(404,
                                                                   "not found")
        mock_di.resolver.unpack.return_value = flavor_mock, utils_mock
        response = self.app.delete('/v1/orm/flavors/123/os_extra_specs',
                                   expect_errors=True)

        # dict_body = json.loads(response.body)
        # my_json = json.loads(dict_body['faultstring'])

        # self.assertEqual(response.status_code, 404)
        # self.assertEqual(my_json['message'], 'not found')


def get_utils_flavor_logic_mock(input_json=None):
    es = models.ExtraSpecsWrapper(input_json["os_extra_specs"])
    utils_mock = MagicMock()
    flavor_logic_mock = MagicMock()
    flavor_logic_mock.add_extra_specs.return_value = es
    flavor_logic_mock.update_extra_specs.return_value = es
    flavor_logic_mock.get_extra_specs_uuid.return_value = es
    utils_mock.audit_trail.return_value = None
    return flavor_logic_mock, utils_mock


flavor_extra_specs_json = {
    "os_extra_specs": {
        "name357": "region_name1",
        "name4467": "2",
        "name66767": "222234556"
    }
}
