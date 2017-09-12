"""get_groups unittests module."""
import json

from orm.services.region_manager.rms.controllers.v2.orm.resources import groups
from orm.tests.unit.rms import FunctionalTest

from mock import MagicMock, patch
from wsme.exc import ClientSideError

res = {"regions": ["aaaa", "bbbb", "ccccc"],
       "name": "mygroup", "id": "any",
       "description": "this is my only for testing"}


group_dict = {'id': 'noq', 'name': 'poq', 'description': 'b', 'regions': ['c']}


class Groups(object):
    """class method."""

    def __init__(self, id=None, name=None, description=None,
                 regions=[], any=None):
        """init function.

        :param regions:
        :return:
        """
        self.id = id
        self.name = name
        self.description = description
        self.regions = regions
        if any:
            self.any = any


class GroupsList(object):
    def __init__(self, groups):
        self.groups = []
        for group in groups:
            self.groups.append(Groups(**group))


class TestGetGroups(FunctionalTest):

    # all success
    @patch.object(groups.GroupService, 'get_groups_data', return_value=Groups(**res))
    @patch.object(groups, 'authentication')
    def test_get_success(self, mock_authentication, result):
        response = self.app.get('/v2/orm/groups/1')
        self.assertEqual(dict(response.json), res)

    # raise exception no content
    @patch.object(groups.GroupService, 'get_groups_data',
                  side_effect=groups.error_base.NotFoundError("no content !!!?"))
    @patch.object(groups.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 404,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '444',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=404))
    @patch.object(groups, 'authentication')
    def test_get_groups_not_found(self, mock_auth, get_err, result):
        temp_request = groups.request
        groups.request = MagicMock()

        response = self.app.get('/v2/orm/groups/1', expect_errors=True)

        groups.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('444', result_json['transaction_id'])
        self.assertEqual(404, result_json['code'])

    # raise general exception
    @patch.object(groups.GroupService, 'get_groups_data', side_effect=Exception("unknown error"))
    @patch.object(groups.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '555',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    @patch.object(groups, 'authentication')
    def test_get_groups_unknown_exception(self, mock_auth, get_err, result):
        temp_request = groups.request
        groups.request = MagicMock()

        response = self.app.get('/v2/orm/groups/1', expect_errors=True)

        groups.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('555', result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])


class TestCreateGroup(FunctionalTest):
    """Main create_group test case."""

    @patch.object(groups, 'request')
    @patch.object(groups.GroupService, 'create_group_in_db')
    @patch.object(groups, 'authentication')
    def test_post_success(self, mock_authentication, mock_create_group,
                          mock_request):
        """Test successful group creation."""
        mock_request.application_url = 'http://localhost'
        response = self.app.post_json('/v2/orm/groups',
                                      {'id': 'd', 'name': 'a',
                                       'description': 'b',
                                       'regions': ['c']})
        # Make sure all keys are in place
        self.assertTrue(all([c in response.json['group'] for c in (
            'created', 'id', 'links')]))

        self.assertEqual(response.json['group']['id'], 'd')
        self.assertEqual(response.json['group']['name'], 'a')
        self.assertEqual(response.json['group']['links']['self'],
                         'http://localhost/v2/orm/groups/d')

    @patch.object(groups.GroupService, 'create_group_in_db', side_effect=groups.error_base.ConflictError)
    @patch.object(groups.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 409,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '333',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=409))
    @patch.object(groups, 'authentication')
    def test_post_group_already_exists(self, mock_auth, get_err,
                                       mock_create_group):
        """Make sure the function returns status code 409 if group exists."""
        temp_request = groups.request
        groups.request = MagicMock()

        response = self.app.post_json('/v2/orm/groups',
                                      {'id': 'noq', 'name': 'poq',
                                       'description': 'b',
                                       'regions': ['c']}, expect_errors=True)

        groups.request = temp_request
        self.assertEqual(response.status_code, 409)


class TestDeleteGroup(FunctionalTest):
    """Main delete group."""

    @patch.object(groups, 'request')
    @patch.object(groups.GroupService, 'delete_group')
    @patch.object(groups, 'authentication')
    def test_delete_group_success(self, auth_mock, mock_delete_group,
                                  mock_request):
        response = self.app.delete('/v2/orm/groups/{id}')
        self.assertEqual(response.status_code, 204)

    @patch.object(groups.GroupService, 'delete_group', side_effect=Exception("any"))
    @patch.object(groups, 'authentication')
    def test_delete_group_error(self, auth_mock, mock_delete_group):
        response = self.app.delete('/v2/orm/groups/{id}', expect_errors=True)
        self.assertEqual(response.status_code, 500)


class TestUpdateGroup(FunctionalTest):
    """Main delete group."""

    def get_error(self, transaction_id, status_code, error_details=None,
                  message=None):
        return ClientSideError(json.dumps({
            'code': status_code,
            'type': 'test',
            'created': '0.0',
            'transaction_id': transaction_id,
            'message': message if message else error_details,
            'details': 'test'
        }), status_code=status_code)

    @patch.object(groups, 'request')
    @patch.object(groups.GroupService, 'update_group',
                  return_value=Groups(**group_dict))
    @patch.object(groups, 'authentication')
    def test_update_group_success(self, auth_mock, mock_delete_group,
                                  mock_request):
        response = self.app.put_json('/v2/orm/groups/id', group_dict)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['group']['id'], group_dict['id'])

    # @patch.object(groups, 'err_utils')
    # @patch.object(groups.GroupService, 'update_group',
    #               side_effect=error_base.NotFoundError(message="any"))
    # @patch.object(groups, 'authentication')
    # def test_update_group_error(self, auth_mock, mock_delete_group,
    #                             mock_err_utils):
    #     mock_err_utils.get_error = self.get_error
    #     response = self.app.put_json('/v2/orm/groups/{id}', group_dict,
    #                                  expect_errors=True)
    #     self.assertEqual(response.status_code, 404)

    @patch.object(groups.GroupService, 'get_all_groups',
                  return_value=GroupsList([res]))
    @patch.object(groups, 'authentication')
    def test_get_all_success(self, mock_authentication, result):
        response = self.app.get('/v2/orm/groups')
        self.assertEqual(dict(response.json), {'groups': [res]})
