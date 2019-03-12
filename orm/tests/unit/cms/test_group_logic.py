from orm.services.customer_manager.cms_rest.data.sql_alchemy\
    import models as sql_models
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.logic import group_logic
import orm.services.customer_manager.cms_rest.model.GroupModels as models
from orm.tests.unit.cms import FunctionalTest

import mock

group = None
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


class RdsStatus(object):

    def __init__(self, status_code=200, status="Success", oy=False):
        self.status_code = status_code
        self.status = status
        self.oy = oy

    def json(self):
        if self.oy:
            return {}
        else:
            return {"status": self.status}


class TestGroupLogic(FunctionalTest):
    def setUp(self):
        global group

        FunctionalTest.setUp(self)
        group_logic.DataManager = get_mock_datamanager
        group_logic.pecan = mock.MagicMock()
        group_logic.utils = mock.MagicMock()
        group_logic.utils.make_transid.return_value = 'some_trans_id'
        group_logic.utils.audit_trail.return_value = None
        group_logic.utils.make_uuid.return_value = 'some_uuid'
        group_logic.utils.get_time_human.return_value = '111'

        group_logic.RdsProxy = mock.MagicMock()
        group_logic.RdsProxy.send_group.return_value = None
        group_logic.RdsProxy.get_status.return_value = RdsStatus()

        group_logic.build_response = mock.MagicMock()

        group = models.Group()

        global flow_type
        flow_type = 0

    def tearDown(self):
        global mock_returns_error
        FunctionalTest.tearDown(self)
        mock_returns_error = False

    def test_create_group_success_with_regions(self):
        group.regions = [models.Region(name="a")]
        group.name = 'Group Name'
        logic = group_logic.GroupLogic()
        logic.create_group(group, 'some_uuid', 'some_trans_id')

        assert data_manager_mock.commit.called
        assert not data_manager_mock.rollback.called

    def test_delete_region_success(self):
        logic = group_logic.GroupLogic()
        logic.delete_region('group_id', 'region_id', 'transaction_is', True,
                            False)

        assert record_mock.delete_region_for_group.called
        assert data_manager_mock.commit.called

    def test_delete_region_success_force_delete(self):
        logic = group_logic.GroupLogic()
        logic.delete_region('group_id', 'region_id', 'transaction_is', True,
                            True)

        assert record_mock.delete_region_for_group.called
        assert data_manager_mock.commit.called

    def test_delete_region_error(self):
        global mock_returns_error
        mock_returns_error = True

        logic = group_logic.GroupLogic()

        self.assertRaises(SystemError, logic.delete_region, 'group_id',
                          'region_id', 'transaction_is', True, False)
        assert data_manager_mock.rollback.called

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

    def test_delete_group_by_uuid_success(self):
        logic = group_logic.GroupLogic()
        logic.delete_group_by_uuid('group_id')

        # Customer found in CMS DB but not found in RDS
        group_logic.RdsProxy.get_status.return_value = RdsStatus(
            status_code=404)
        logic.delete_group_by_uuid('group_id')

    def test_delete_group_by_uuid_not_found(self):
        global flow_type
        # Change the flow to "customer not found in CMS DB"
        flow_type = 1
        logic = group_logic.GroupLogic()

        # test that ErrorStatus exception is raised when no customer found
        with self.assertRaises(group_logic.ErrorStatus):
            logic.delete_group_by_uuid('group_id')

    def test_delete_group_by_uuid_errors(self):
        global mock_returns_error
        mock_returns_error = True
        logic = group_logic.GroupLogic()
        self.assertRaises(SystemError, logic.delete_group_by_uuid, 'group_id')

        # RDS returned an empty json
        mock_returns_error = False
        group_logic.RdsProxy.get_status.return_value = RdsStatus(oy=True)
        self.assertRaises(group_logic.ErrorStatus,
                          logic.delete_group_by_uuid,
                          'group_id')

        # RDS returned 500
        group_logic.RdsProxy.get_status.return_value = RdsStatus(
            status_code=500)
        self.assertRaises(group_logic.ErrorStatus,
                          logic.delete_group_by_uuid,
                          'group_id')

        # RDS returned Error status
        group_logic.RdsProxy.get_status.return_value = RdsStatus(
            status='Error')
        self.assertRaises(group_logic.ErrorStatus,
                          logic.delete_group_by_uuid,
                          'group_id')

    def test_delete_group_by_uuid_conflict(self):
        global flow_type
        flow_type = 2
        logic = group_logic.GroupLogic()
        self.assertRaises(group_logic.ErrorStatus, logic.delete_group_by_uuid,
                          'group_id')


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
        record_mock.delete_region_for_group.return_value = None
        record_mock.delete_group_by_uuid.return_value = None

        if flow_type == 1:
            record_mock.read_group_by_uuid.return_value = None
            data_manager_mock.get_group_by_uuid_or_name.return_value = None
        elif flow_type == 2:
            q = mock.MagicMock()
            q.get_group_regions.return_value = [mock.MagicMock()]
            record_mock.read_group_by_uuid.return_value = q
            record_mock.delete_group_by_uuid.side_effect = SystemError()
    else:
        record_mock.read_group_by_uuid.side_effect = SystemError()
        record_mock.delete_region_for_group.side_effect = SystemError()

    data_manager_mock.get_record.return_value = record_mock
    return data_manager_mock
