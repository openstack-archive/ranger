from orm.services.customer_manager.cms_rest.data.sql_alchemy import models as sql_models
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.logic import group_logic
import orm.services.customer_manager.cms_rest.model.GroupModels as models
from orm.tests.unit.cms import FunctionalTest

import mock

data_manager_mock = None
record_mock = None
mock_returns_error = False
flow_type = 0


STATUS_JSON = {
    "regions": [
        {
            "status": "Success",
            "region": "GRP1",
            "error_code": "",
            "error_msg": ""
        }
    ],
    "status": "Success"
}


class TestGroupLogic(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)
        group_logic.DataManager = get_mock_datamanager
        group_logic.pecan = mock.MagicMock()

        global flow_type
        flow_type = 0

    def tearDown(self):
        global mock_returns_error
        FunctionalTest.tearDown(self)
        mock_returns_error = False

    def test_get_group_list_by_criteria(self):
        logic = group_logic.GroupLogic()
        result = logic.get_group_list_by_criteria(None, None, None, None)
        self.assertTrue(data_manager_mock.get_record.called)
        self.assertTrue(record_mock.get_groups_by_criteria.called)

    def test_get_group_success(self):
        logic = group_logic.GroupLogic()
        get_mock = mock.MagicMock()
        get_mock.json.return_value = STATUS_JSON
        group_logic.requests.get = mock.MagicMock(return_value=get_mock)
        logic.get_group('group_id')
        self.assertTrue(data_manager_mock.get_group_by_uuid_or_name.called)

    def test_get_group_not_found(self):
        global flow_type
        flow_type = 1
        logic = group_logic.GroupLogic()
        self.assertRaises(ErrorStatus, logic.get_group, 'group_id')
        self.assertTrue(data_manager_mock.get_group_by_uuid_or_name.called)


def get_mock_datamanager():
    global data_manager_mock
    global record_mock

    sql_group = sql_models.Groups(name='a')
    sql_group.group_regions = []

    data_manager_mock = mock.MagicMock()
    record_mock = mock.MagicMock()
    record_mock.get_groups_by_criteria.return_value = [sql_group]

    def _get_group():
        def mock_to_wsme():
            return models.Group(regions=[models.Region()])

        sql_group = sql_models.Groups()
        sql_group.to_wsme = mock_to_wsme
        sql_group.uuid = '1234'
        sql_group.status = 'Success'
        sql_group.name = 'GRP1'

        return sql_group

    if not mock_returns_error:
        data_manager_mock.get_group_by_uuid_or_name.return_value = _get_group()

        if flow_type == 1:
            record_mock.read_group_by_uuid.return_value = None
            data_manager_mock.get_group_by_uuid_or_name.return_value = None
        elif flow_type == 2:
            q = mock.MagicMock()
            q.get_group_regions.return_value = [mock.MagicMock()]
            record_mock.read_group_by_uuid.return_value = q
    else:
        record_mock.read_group_by_uuid.side_effect = SystemError()

    data_manager_mock.get_record.return_value = record_mock
    return data_manager_mock
