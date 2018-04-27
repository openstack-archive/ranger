from orm.services.customer_manager.cms_rest.data.sql_alchemy import models as sql_models
from orm.services.customer_manager.cms_rest.logic import customer_logic
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
import orm.services.customer_manager.cms_rest.model.Models as models
from orm.tests.unit.cms import FunctionalTest

import mock

customer = None
data_manager_mock = None
record_mock = None
mock_returns_error = False
flow_type = 0
rowcount = 1


class resultobj():
    def __init__(self, rowcount=1):
        self.rowcount = rowcount


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


class TestCustomerLogic(FunctionalTest):
    def setUp(self):
        global customer

        FunctionalTest.setUp(self)
        customer_logic.DataManager = get_mock_datamanager
        customer_logic.pecan = mock.MagicMock()

        customer_logic.utils = mock.MagicMock()
        customer_logic.utils.make_transid.return_value = 'some_trans_id'
        customer_logic.utils.audit_trail.return_value = None
        customer_logic.utils.make_uuid.return_value = 'some_uuid'
        customer_logic.utils.get_time_human.return_value = '1337'

        customer_logic.RdsProxy = mock.MagicMock()
        customer_logic.RdsProxy.send_customer.return_value = None
        customer_logic.RdsProxy.get_status.return_value = RdsStatus()

        customer_logic.build_response = mock.MagicMock()

        customer = models.Customer()
        user = models.User()
        customer.users = [user, models.User()]
        user.role = ['user', 'admin']

        global flow_type
        flow_type = 0

    def tearDown(self):
        global mock_returns_error
        FunctionalTest.tearDown(self)

        mock_returns_error = False

    def test_create_customer_success_with_regions(self):
        customer.regions = [models.Region(name="a")]
        customer.name = 'Cust Name'
        logic = customer_logic.CustomerLogic()
        logic.create_customer(customer, 'some_uuid', 'some_trans_id')

        # sql_customer, trans_id = customer_logic.RdsProxy.send_customer.call_args_list[0][0]
        # assert trans_id is 'some_trans_id'
        # assert type(sql_customer) is sql_models.Customer
        assert data_manager_mock.commit.called
        assert not data_manager_mock.rollback.called

    def test_add_regions_action(self):
        regions = [models.Region(), models.Region()]
        logic = customer_logic.CustomerLogic()
        logic.add_regions('some_uuid', regions, 'some_trans_id')

        res = customer_logic.RdsProxy.send_customer.call_args_list

    def test_create_customer_add_all_default_users(self):
        customer.name = 'Cust Name'
        logic = customer_logic.CustomerLogic()
        logic.create_customer(customer, 'some_uuid', 'some_trans_id')

        assert data_manager_mock.add_user.call_count == 2

    def test_create_customer_fail_rollback(self):
        global mock_returns_error
        mock_returns_error = True

        customer.name = 'Cust Name'
        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.create_customer, customer, 'some_uuid', 'some_trans_id')

    def test_create_customer_with_blank_name(self):
        global mock_returns_error
        mock_returns_error = True

        customer.name = ''
        logic = customer_logic.CustomerLogic()

        self.assertRaises(customer_logic.ErrorStatus,
                          logic.create_customer,
                          customer, 'some_uuid', 'some_trans_id')

    def test_update_customer_success(self):
        customer.name = 'Cust Name'
        logic = customer_logic.CustomerLogic()
        logic.update_customer(customer, 'some_uuid', 'some_trans_id')

        assert record_mock.delete_by_primary_key.called
        assert data_manager_mock.commit.called
        assert not data_manager_mock.rollback.called

    def test_update_customer_fail_rollback(self):
        global mock_returns_error
        mock_returns_error = True

        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.update_customer, customer, 'some_uuid', 'some_trans_id')

    def test_add_users_success(self):
        logic = customer_logic.CustomerLogic()
        users = [models.User(), models.User()]

        logic.add_users('some_uuid', 'some_region', users, 'some_transaction')

        assert data_manager_mock.add_user.call_count == 2
        assert data_manager_mock.commit.called

    def test_add_users_error(self):
        global mock_returns_error
        mock_returns_error = True

        logic = customer_logic.CustomerLogic()
        users = [models.User()]

        self.assertRaises(SystemError, logic.add_users, 'id', 'region', users, 'trans_id')

    def test_replace_users_success(self):
        logic = customer_logic.CustomerLogic()
        users = [models.User(), models.User()]

        logic.replace_users('some_uuid', 'some_region', users, 'some_transaction')

        assert record_mock.delete_all_users_from_region.called
        assert data_manager_mock.add_user.called
        assert data_manager_mock.commit.called

    def test_replace_users_error(self):
        global mock_returns_error
        mock_returns_error = True

        logic = customer_logic.CustomerLogic()
        users = [models.User()]

        self.assertRaises(SystemError, logic.replace_users, 'id', 'region', users, 'trans_id')

    def test_add_customer_with_default_users(self):
        default_quota = models.Quota()
        customer.defaultQuotas = [default_quota]

        default_region = models.Region()
        customer.regions = [default_region]
        customer.name = 'Cust Name'

        default_user = models.User()
        default_user.role = ['user', 'admin']

        default_region.users = [default_user]

        logic = customer_logic.CustomerLogic()

        logic.create_customer(customer, 'some_uuid', 'some_trans_id')

        assert data_manager_mock.add_user.called

    def test_add_users_with_roles_success(self):
        user = models.User()
        user.role = ['user', 'admin']

        users = [user, models.User()]

        logic = customer_logic.CustomerLogic()
        logic.add_users('some_uuid', 'region_name', users, 'some_trans_id')

        assert data_manager_mock.add_user.call_count == 2
        assert data_manager_mock.add_role.call_count == 2
        assert data_manager_mock.commit.called

    def test_delete_users_success(self):
        logic = customer_logic.CustomerLogic()
        logic.delete_users('customer_id', 'region_id', 'user_id', 'transaction_is')

        assert record_mock.delete_user_from_region.called
        assert data_manager_mock.commit.called
        assert customer_logic.RdsProxy.send_customer.called

    def test_delete_users_fail_notfound(self):
        global rowcount
        rowcount = 0
        logic = customer_logic.CustomerLogic()
        with self.assertRaises(customer_logic.ErrorStatus):
            logic.delete_users('customer_id', 'region_id', 'user_id',
                               'transaction_is')
        rowcount = 1
        assert record_mock.delete_user_from_region.called
        assert data_manager_mock.rollback.called

    def test_delete_users_error(self):
        global mock_returns_error
        mock_returns_error = True

        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.delete_users, 'customer_id', 'region_id', 'user_id', 'transaction_is')
        assert data_manager_mock.rollback.called

    def test_add_default_users_with_regions_success(self):
        user = models.User()
        user.role = ['user', 'admin']

        users = [user, models.User()]
        logic = customer_logic.CustomerLogic()

        logic.add_default_users('customer_uuid', users, 'transaction_id')

        assert data_manager_mock.commit.called
        assert data_manager_mock.add_user.call_count == 2
        assert data_manager_mock.add_role.call_count == 2

    def test_add_default_users_no_regions_success(self):
        user = models.User()
        user.role = ['user', 'admin']

        users = [user, models.User()]
        logic = customer_logic.CustomerLogic()

        logic.add_default_users('customer_uuid', users, 'transaction_id')

        assert data_manager_mock.commit.called
        assert not customer_logic.RdsProxy.send_customer.called
        assert data_manager_mock.add_user.call_count == 2
        assert data_manager_mock.add_role.call_count == 2

    def test_add_default_users_fail(self):
        global mock_returns_error
        mock_returns_error = True
        users = [models.User(), models.User()]

        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.add_default_users, 'customer_uuid', users, 'transaction_id')
        assert data_manager_mock.rollback.called

    def test_replace_default_users_no_regions_success(self):
        user = models.User()
        user.role = ['user', 'admin']

        users = [user, models.User()]
        logic = customer_logic.CustomerLogic()

        logic.replace_default_users('customer_uuid', users, 'transaction_id')

        assert data_manager_mock.commit.called
        assert record_mock.delete_all_users_from_region.called
        assert not customer_logic.RdsProxy.send_customer.called
        assert data_manager_mock.add_user.call_count == 2
        assert data_manager_mock.add_role.call_count == 2

    def test_replace_default_users_fail(self):
        global mock_returns_error
        mock_returns_error = True
        users = [models.User(), models.User()]

        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.replace_default_users, 'id', users, 'trans_id')
        assert data_manager_mock.rollback.called

    def test_delete_default_users_success(self):
        logic = customer_logic.CustomerLogic()
        logic.delete_default_users('customer_id', 'user_id', 'transaction_is')

        assert record_mock.delete_user_from_region.called
        assert data_manager_mock.commit.called

    def test_delete_default_users_fail_notfound(self):
        global rowcount
        rowcount = 0
        logic = customer_logic.CustomerLogic()
        with self.assertRaises(customer_logic.NotFound):
            logic.delete_default_users('customer_id', 'user_id',
                                       'transaction_is')
        rowcount = 1
        assert record_mock.delete_user_from_region.called
        assert data_manager_mock.rollback.called

    def test_delete_default_users_error(self):
        global mock_returns_error
        mock_returns_error = True

        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.delete_default_users, 'customer_id', 'user_id', 'transaction_is')
        assert data_manager_mock.rollback.called

    def test_add_regions_success(self):
        regions = [models.Region(), models.Region()]
        logic = customer_logic.CustomerLogic()

        logic.add_regions('customer_uuid', regions, 'transaction_id')

        assert data_manager_mock.commit.called
        assert customer_logic.RdsProxy.send_customer_dict.called
        # assert data_manager_mock.add_region.called

    def test_add_regions_fail(self):
        global mock_returns_error
        mock_returns_error = True
        regions = [models.Region(), models.Region()]
        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.add_regions, 'customer_uuid', regions, 'transaction_id')
        assert data_manager_mock.rollback.called

    def test_replace_regions_success(self):
        regions = [models.Region(), models.Region()]
        logic = customer_logic.CustomerLogic()

        logic.replace_regions('customer_uuid', regions, 'transaction_id')

        assert data_manager_mock.commit.called
        assert customer_logic.RdsProxy.send_customer_dict.called
        assert record_mock.delete_all_regions_for_customer.called

    def test_replace_regions_fail(self):
        global mock_returns_error
        mock_returns_error = True
        regions = [models.Region(), models.Region()]
        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.replace_regions, 'customer_uuid', regions, 'transaction_id')
        assert data_manager_mock.rollback.called

    def test_delete_regions_success(self):
        logic = customer_logic.CustomerLogic()
        logic.delete_region('customer_id', 'region_id', 'transaction_is', True, False)

        assert record_mock.delete_region_for_customer.called
        assert data_manager_mock.commit.called

    def test_delete_regions_success_force_delete(self):
        logic = customer_logic.CustomerLogic()
        logic.delete_region('customer_id', 'region_id', 'transaction_is', True, True)

        assert record_mock.delete_region_for_customer.called
        assert data_manager_mock.commit.called

    def test_delete_regions_error(self):
        global mock_returns_error
        mock_returns_error = True

        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.delete_region, 'customer_id',
                          'region_id', 'transaction_is', True, False)
        assert data_manager_mock.rollback.called

    def test_get_customer_list_by_criteria(self):
        logic = customer_logic.CustomerLogic()
        result = logic.get_customer_list_by_criteria(None, None, None, None,
                                                     {"key:value"})

    def test_delete_customer_by_uuid_success(self):
        logic = customer_logic.CustomerLogic()
        logic.delete_customer_by_uuid('customer_id')

        # Customer found in CMS DB but not found in RDS
        customer_logic.RdsProxy.get_status.return_value = RdsStatus(
            status_code=404)
        logic.delete_customer_by_uuid('customer_id')

    def test_delete_customer_by_uuid_not_found(self):
        global flow_type
        # Change the flow to "customer not found in CMS DB"
        flow_type = 1
        logic = customer_logic.CustomerLogic()

        # test that ErrorStatus exception is raised when no customer found
        with self.assertRaises(customer_logic.ErrorStatus):
            logic.delete_customer_by_uuid('customer_id')

    def test_delete_customer_by_uuid_errors(self):
        global mock_returns_error
        mock_returns_error = True
        logic = customer_logic.CustomerLogic()
        self.assertRaises(SystemError, logic.delete_customer_by_uuid, 'customer_id')

        # RDS returned an empty json
        mock_returns_error = False
        customer_logic.RdsProxy.get_status.return_value = RdsStatus(oy=True)
        self.assertRaises(customer_logic.ErrorStatus,
                          logic.delete_customer_by_uuid,
                          'customer_id')

        # RDS returned 500
        customer_logic.RdsProxy.get_status.return_value = RdsStatus(
            status_code=500)
        self.assertRaises(customer_logic.ErrorStatus,
                          logic.delete_customer_by_uuid,
                          'customer_id')

        # RDS returned Error status
        customer_logic.RdsProxy.get_status.return_value = RdsStatus(
            status='Error')
        self.assertRaises(customer_logic.ErrorStatus,
                          logic.delete_customer_by_uuid,
                          'customer_id')

    def test_delete_customer_by_uuid_conflict(self):
        global flow_type
        flow_type = 2
        logic = customer_logic.CustomerLogic()
        self.assertRaises(customer_logic.ErrorStatus, logic.delete_customer_by_uuid,
                          'customer_id')

    def test_enable_success(self):
        logic = customer_logic.CustomerLogic()
        logic.enable('customer_id', models.Enabled(True), 'transaction_is')

        self.assertTrue(record_mock.read_customer_by_uuid.called)
        self.assertTrue(customer_logic.RdsProxy.send_customer.called)

    def test_enable_error(self):
        global mock_returns_error
        mock_returns_error = True

        logic = customer_logic.CustomerLogic()

        self.assertRaises(SystemError, logic.enable, 'id', models.Enabled(True), 'trans_id')
        self.assertTrue(data_manager_mock.rollback.called)

    def test_get_customer_success(self):
        logic = customer_logic.CustomerLogic()
        get_mock = mock.MagicMock()
        get_mock.json.return_value = STATUS_JSON
        customer_logic.requests.get = mock.MagicMock(return_value=get_mock)
        logic.get_customer('customer_id')

        self.assertTrue(data_manager_mock.get_customer_by_uuid_or_name.called)

    def test_get_customer_not_found(self):
        global flow_type
        flow_type = 1
        # customer_logic.requests.get = mock.MagicMock(return_value=None)

        logic = customer_logic.CustomerLogic()

        self.assertRaises(ErrorStatus, logic.get_customer, 'id')


def get_mock_datamanager():
    global data_manager_mock
    global record_mock
    global rowcount

    sql_customer = sql_models.Customer(name='a')
    sql_customer.customer_customer_regions = []

    sql_customer.add_default_users_to_empty_regions = sql_customer

    data_manager_mock = mock.MagicMock()
    record_mock = mock.MagicMock()
    record_mock.get_customers_by_criteria.return_value = [sql_customer]

    def _get_proxy_dict():
        return {
            "uuid": 'a',
            "name": 'a',
            "description": 'a',
            "enabled": 1,
            "regions": []
        }

    def _get_customer():
        def mock_to_wsme():
            return models.Customer(regions=[models.Region(name='DPK', status='Success')])

        def mock_get_real():
            return True

        sql_customer = sql_models.Customer()
        sql_customer.get_real_customer_regions = mock_get_real
        sql_customer.to_wsme = mock_to_wsme
        sql_customer.uuid = '1337'
        sql_customer.status = 'Success'
        sql_customer.name = 'DPK'

        return sql_customer

    def _add_customer(*args, **kwargs):
        global sql_customer
        sql_customer = sql_models.Customer()
        sql_customer.customer_customer_regions = [sql_models.CustomerRegion(region_id=-1)]
        sql_customer.customer_customer_regions.customer_region_user_roles = [sql_models.UserRole()]
        sql_customer.add_default_users_to_empty_regions = sql_customer
        sql_customer.get_proxy_dict = _get_proxy_dict
        return sql_customer

    def _update_customer(*args, **kwargs):
        global sql_customer
        sql_customer = sql_models.Customer(name='a')
        sql_customer.customer_customer_regions = [sql_models.CustomerRegion(region_id=-1)]
        sql_customer.customer_customer_regions.customer_region_user_roles = [sql_models.UserRole()]
        sql_customer.add_default_users_to_empty_regions = sql_customer
        sql_customer.get_proxy_dict = _get_proxy_dict
        return sql_customer

    def _add_region(*args, **kwargs):
        global sql_customer
        region = sql_models.Region()

        # sql_customer.customer_customer_regions.append(region)
        return region

    def _add_users(*args, **kwargs):
        global sql_customer
        users = sql_models.UserRole()

        sql_customer.customer_customer_regions.customer_region_user_roles = users
        return users

    if not mock_returns_error:
        data_manager_mock.add_customer = _add_customer
        data_manager_mock.update_customer = _update_customer
        data_manager_mock.add_region = _add_region
        data_manager_mock.add_user.return_value = sql_models.CmsUser()
        data_manager_mock.get_customer_by_uuid_or_name.return_value = _get_customer()

        record_mock.delete_region_for_customer.return_value = None
        record_mock.delete_customer_by_uuid.return_value = None
        if flow_type == 1:
            record_mock.read_customer_by_uuid.return_value = None
            data_manager_mock.get_customer_by_uuid_or_name.return_value = None
        elif flow_type == 2:
            q = mock.MagicMock()
            q.get_real_customer_regions.return_value = [mock.MagicMock()]
            record_mock.read_customer_by_uuid.return_value = q

        record_mock.delete_user_from_region.return_value = resultobj(rowcount)
    else:
        record_mock.read_customer_by_uuid.side_effect = SystemError()
        data_manager_mock.add_customer.side_effect = SystemError()
        data_manager_mock.add_user.side_effect = SystemError()
        data_manager_mock.add_region.side_effect = SystemError()

        record_mock.delete_region_for_customer.side_effect = SystemError()
        record_mock.delete_user_from_region.side_effect = SystemError()
        record_mock.delete_customer_by_uuid.side_effect = SystemError()

    data_manager_mock.get_record.return_value = record_mock
    data_manager_mock.add_user.return_value = sql_models.CmsUser()
    data_manager_mock.add_role.return_value = sql_models.CmsRole()

    data_manager_mock.get_customer_by_id.return_value = sql_customer

    return data_manager_mock


STATUS_JSON = {
    "regions": [
        {
            "status": "Success",
            "region": "DPK",
            "error_code": "",
            "error_msg": ""
        }
    ],
    "status": "Success"
}
