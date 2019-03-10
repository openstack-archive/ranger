import mock
import requests

from orm.services.customer_manager.cms_rest.controllers.v1.orm.group\
    import root
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model import GroupModels
from orm.tests.unit.cms import FunctionalTest
from wsme.exc import ClientSideError

group_logic_mock = None


class TestGroupController(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        root.authentication = mock.MagicMock()

        root.GroupLogic = get_mock_group_logic
        root.GroupLogic.return_error = 0

        root.utils = mock.MagicMock()
        root.utils.make_transid.return_value = 'some_trans_id'
        root.utils.audit_trail.return_value = None
        root.utils.make_uuid.return_value = 'some_uuid'

        root.err_utils = mock.MagicMock()

    def tearDown(self):
        FunctionalTest.tearDown(self)

    def test_create_group(self):
        # given
        requests.post = mock.MagicMock(return_value=ResponseMock(201))

        # when
        response = self.app.post_json('/v1/orm/groups', GROUP_JSON)

        # assert
        assert response.status_int == 201
        assert root.utils.audit_trail.called
        assert root.utils.create_or_validate_uuid.called
        assert group_logic_mock.create_group_called

    def test_create_group_fail(self):
        # given
        requests.post = mock.MagicMock()

        root.GroupLogic.return_error = 1

        root.err_utils.get_error = mock.MagicMock(
            return_value=ClientSideError("blabla", 500))
        # when
        response = self.app.post_json('/v1/orm/groups',
                                      GROUP_JSON, expect_errors=True)
        # assert
        self.assertEqual(response.status_int, 500)

    def test_get_group(self):
        # given
        requests.get = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.get('/v1/orm/groups/some_id')

        # assert
        assert response.status_int == 200
        assert group_logic_mock.get_group.called

    def test_get_group_fail_bad_request(self):
        # given
        requests.put = mock.MagicMock()
        root.GroupLogic.return_error = 1
        root.err_utils.get_error = mock.MagicMock(
            return_value=ClientSideError("blabla", 500))

        # when
        response = self.app.get('/v1/orm/groups/some_id', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)
        assert group_logic_mock.get_group.called

    def test_get_group_fail(self):
        # given
        requests.put = mock.MagicMock()
        root.GroupLogic.return_error = 2
        root.err_utils.get_error = mock.MagicMock(
            return_value=ClientSideError("blabla", 404))

        # when
        response = self.app.get('/v1/orm/groups/some_id', expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 404)
        assert group_logic_mock.get_group.called

    def test_get_list_group(self):
        # given
        requests.get = mock.MagicMock(return_value=ResponseMock(200))

        # when
        response = self.app.get('/v1/orm/groups?region=region')

        # assert
        assert group_logic_mock.get_group_list_by_criteria.called

    def test_get_list_group_fail(self):
        # given
        requests.get = mock.MagicMock()
        root.GroupLogic.return_error = 1
        root.err_utils.get_error = mock.MagicMock(
            return_value=ClientSideError("blabla", 500))

        # when
        response = self.app.get('/v1/orm/groups?region=region',
                                expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)

    def test_get_list_group_bad_request(self):
        # given
        requests.get = mock.MagicMock()
        root.GroupLogic.return_error = 2
        root.err_utils.get_error = mock.MagicMock(
            return_value=ClientSideError("blabla", 500))

        # when
        response = self.app.get('/v1/orm/groups?region=region',
                                expect_errors=True)

        # assert
        self.assertEqual(response.status_int, 500)


def get_mock_group_logic():
    global group_logic_mock
    group_logic_mock = mock.MagicMock()

    if root.GroupLogic.return_error == 0:
        res = GroupModels.GroupResultWrapper(transaction_id='1',
                                             id='1',
                                             links={},
                                             updated=None,
                                             created='1')
        list_res = GroupModels.GroupSummaryResponse()
        list_res.groups.append(
            GroupModels.GroupSummary(name='1', id='1', description='1'))
        group_logic_mock.get_group.return_value = GroupModels.Group(
            **RET_GROUP_JSON)
        group_logic_mock.get_group_list_by_criteria.return_value = list_res
        group_logic_mock.create_group.return_value = res

    elif root.GroupLogic.return_error == 1:
        group_logic_mock.create_group.side_effect = SystemError()
        group_logic_mock.get_group.side_effect = SystemError()
        group_logic_mock.get_group_list_by_criteria.side_effect = SystemError()

    else:
        group_logic_mock.get_group.side_effect = ErrorStatus(status_code=404)
        group_logic_mock.get_group_list_by_criteria.side_effect = ErrorStatus(
            status_code=404)

    return group_logic_mock


class ResponseMock:
    def __init__(self, status_code=200):
        self.status_code = status_code


GROUP_JSON = {
    "description": "Group description",
    "enabled": True,
    "name": "myGroup",
    "domainId": 1,
    "regions": [
        {
            "name": "SAN1",
            "type": "single"
        }
    ]
}

RET_GROUP_JSON = {
    "description": "Group description",
    "name": "myName",
    "domainId": 1,
    "enabled": True,
    "regions": [GroupModels.Region()]
}
