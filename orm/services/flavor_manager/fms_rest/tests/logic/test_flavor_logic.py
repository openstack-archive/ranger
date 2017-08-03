from fms_rest.data.sql_alchemy import db_models
from fms_rest.data.wsme import models
from fms_rest.data.wsme.models import *
from fms_rest.logic.error_base import NotFoundError
import fms_rest.logic.flavor_logic as flavor_logic
from fms_rest.tests import FunctionalTest
from mock import MagicMock, patch
from orm_common.injector import injector


class OES():

    def __init__(self):
        pass

    def to_db_model(self):
        return None

error = None
FLAVOR_MOCK = None


class TestFlavorLogic(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

        global FLAVOR_MOCK
        FLAVOR_MOCK = MagicMock()

        injector.override_injected_dependency(('data_manager', get_datamanager_mock))
        injector.override_injected_dependency(('rds_proxy', rds_proxy_mock))

    def tearDown(self):
        global error
        error = None
        FunctionalTest.tearDown(self)

    def test_get_fixed_uuid_valid_uuid(self):
        # With dashes
        test_uuid = 'f8391e94-b332-4d7f-956c-07c6096b9140'
        expected_result = test_uuid.replace('-', '')
        self.assertEqual(expected_result, flavor_logic.get_fixed_uuid(
            test_uuid))

        # Without dashes
        test_uuid = 'f8391e94b3324d7f956c07c6096b9140'
        self.assertEqual(test_uuid, flavor_logic.get_fixed_uuid(test_uuid))

    def test_get_fixed_uuid_not_a_uuid(self):
        self.assertRaises(flavor_logic.ErrorStatus,
                          flavor_logic.get_fixed_uuid, 'test')

    def test_get_fixed_uuid_not_a_version_4_uuid(self):
        self.assertRaises(flavor_logic.ErrorStatus,
                          flavor_logic.get_fixed_uuid,
                          'f8391e94-b332-1d7f-956c-07c6096b9140')

    @patch.object(flavor_logic, 'FlavorWrapper')
    def test_create_flavor_duplicate_entry(self, mock_flavorwrapper):
        mock_flavorwrapper.from_db_model.return_value = get_flavor_mock()
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))
        flavor = get_flavor_mock()
        flavor.flavor.validate_model = MagicMock(
            side_effect=flavor_logic.ErrorStatus(409, 'Duplicate entry'))
        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.create_flavor,
                          flavor, 'uuid', 'transaction')

    @patch.object(flavor_logic, 'FlavorWrapper')
    def test_create_flavor_success(self, mock_flavorwrapper):
        mock_flavorwrapper.from_db_model.return_value = get_flavor_mock()
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))

        res_flavor = flavor_logic.create_flavor(get_flavor_mock(), 'uuid',
                                                'transaction')
        self.assertEqual(res_flavor.flavor.profile, 'N1')
        self.assertEqual(res_flavor.flavor.ram, '1024')
        self.assertEqual(res_flavor.flavor.vcpus, '1')
        self.assertEqual(res_flavor.flavor.series, 'ss')
        self.assertEqual(res_flavor.flavor.id, 'g')

        flavor = get_flavor_mock()
        flavor.flavor.ephemeral = ''
        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.create_flavor,
                          flavor, 'uuid', 'transaction')

        flavor.flavor.validate_model = MagicMock()
        res_flavor = flavor_logic.create_flavor(flavor, 'uuid',
                                                'transaction')
        self.assertEqual(res_flavor.flavor.profile, 'N1')
        self.assertEqual(res_flavor.flavor.ram, '1024')
        self.assertEqual(res_flavor.flavor.vcpus, '1')
        self.assertEqual(res_flavor.flavor.series, 'ss')
        self.assertEqual(res_flavor.flavor.id, 'g')

    #
    # def test_get_flavor_by_uuid_check_statuses_ok(self):
    #     flavor_logic.get_flavor_by_uuid("SampleUUId")

    @patch.object(flavor_logic, 'ExtraSpecsWrapper', return_value=MagicMock())
    def test_get_extra_specs_success(self, extra_spec_wrapper):
        global error
        error = 3
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        extra_spec_wrapper.from_db_model.return_value = {"key", "value"}
        result = flavor_logic.get_extra_specs_uuid(123, "transaction_id")
        self.assertEqual({"key", "value"}, result)

    @patch.object(flavor_logic, 'ExtraSpecsWrapper', return_value=MagicMock())
    def test_get_extra_specs_not_found(self, extra_spec_wrapper):
        global error
        error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(flavor_logic.NotFoundError):
            flavor_logic.get_extra_specs_uuid(123, "transaction_id")

    @patch.object(flavor_logic, 'ExtraSpecsWrapper', return_value=MagicMock())
    def test_get_extra_specs_general_error(self, extra_spec_wrapper):
        global error
        error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(Exception) as cm:
            flavor_logic.get_extra_specs_uuid(123, "transaction_id")

    @patch.object(flavor_logic, 'send_to_rds_if_needed', return_value=True)
    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    def test_delete_extra_specs_success(self, mock_flavorwrapper,
                                        mock_send_rds):
        flavor_logic.delete_extra_specs(123, "transaction_id")

    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    def test_delete_extra_specs_not_found(self, mock_flavorwrapper):
        global error
        error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(flavor_logic.NotFoundError):
            flavor_logic.delete_extra_specs(123, "transaction_id")

    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    def test_delete_extra_specs_bad_req(self, mock_flavorwrapper):
        global error
        error = 3
        extra_spec_needed = db_models.FlavorExtraSpec("key1", "value")
        get_extra_spec_needed = MagicMock()
        get_extra_spec_needed.get_extra_spec_needed.return_value = [extra_spec_needed]
        mock_flavorwrapper.from_db_model.return_value = get_extra_spec_needed
        with self.assertRaises(ErrorStatus):
            flavor_logic.delete_extra_specs(123, "transaction_id", "key1")

    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    def test_delete_extra_specs_one(self, mock_flavorwrapper):
        global error
        error = 3
        extra_spec_needed = db_models.FlavorExtraSpec("key1", "value")
        get_extra_spec_needed = MagicMock()
        get_extra_spec_needed.get_extra_spec_needed.return_value = [
            extra_spec_needed]
        mock_flavorwrapper.from_db_model.return_value = get_extra_spec_needed
        flavor_logic.delete_extra_specs(123, "transaction_id", "key2")

    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    def test_delete_extra_specs_general_error(self, mock_flavorwrapper):
        global error
        error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(Exception) as cm:
            flavor_logic.delete_extra_specs(123, "transaction_id")

    @patch.object(flavor_logic.ExtraSpecsWrapper, 'from_db_model',
                  return_value=True)
    @patch.object(flavor_logic, 'send_to_rds_if_needed', return_value=True)
    def test_add_extra_specs_success(self, mock_send_rds, extra_specs_wrapper):
        flavor_logic.add_extra_specs(123, OES(), "transaction_id")

    def test_add_extra_specs_not_found(self):
        global error
        error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(flavor_logic.NotFoundError):
            flavor_logic.add_extra_specs(123, OES(), "transaction_id")

    def test_add_extra_specs_gen_exp(self):
        global error
        error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(Exception):
            flavor_logic.add_extra_specs(123, OES(), "transaction_id")

    @patch.object(flavor_logic.ExtraSpecsWrapper, 'from_db_model')
    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    @patch.object(flavor_logic, 'send_to_rds_if_needed', return_value=True)
    def test_update_extra_specs_success(self, mock_send_rds,
                                        flavor_wrapper,
                                        extra_specs_wrapper):
        extra_specs_wrapper.return_value = extra_specs_json
        result = flavor_logic.update_extra_specs(123, OES(), "transaction_id")
        self.assertEqual(result, extra_specs_json)

    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    @patch.object(flavor_logic, 'send_to_rds_if_needed', return_value=True)
    def test_update_extra_specs_not_found(self, mock_send_rds,
                                          extra_specs_wrapper):
        global error
        error = 1
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(flavor_logic.NotFoundError):
            flavor_logic.update_extra_specs(123, OES(), "transaction_id")

    @patch.object(flavor_logic, 'FlavorWrapper', return_value=MagicMock())
    @patch.object(flavor_logic, 'send_to_rds_if_needed', return_value=True)
    def test_update_extra_specs_any_except(self, mock_send_rds,
                                           extra_specs_wrapper):
        global error
        error = 2
        injector.override_injected_dependency(
            ('flavor_logic', get_datamanager_mock()))
        with self.assertRaises(Exception):
            flavor_logic.update_extra_specs(123, OES(), "transaction_id")

    def test_add_tags_success(self):
        global error
        error = 0
        datamanager = get_datamanager_mock()
        injector.override_injected_dependency(('data_manager', datamanager))

        tag = TagsWrapper(tags={'a': 'b'})
        ret = flavor_logic.add_tags('some_id', tag, 'trans_id')

        assert datamanager.return_value.commit.called

    def test_add_tags_not_found(self):
        global error
        error = 1
        injector.override_injected_dependency(('data_manager', get_datamanager_mock))

        self.assertRaises(NotFoundError, flavor_logic.add_tags, 'a', None, 'a')

    def test_add_tags_error(self):
        global error
        error = 2
        injector.override_injected_dependency(('data_manager', get_datamanager_mock))

        self.assertRaises(Exception, flavor_logic.add_tags, 'a', None, 'a')

    @patch.object(flavor_logic.FlavorWrapper, 'from_db_model')
    def test_get_tags_success(self, mock_from_db_model):
        my_flavor = MagicMock()
        my_flavor.flavor.tag = {'test': 'A'}
        mock_from_db_model.return_value = my_flavor

        global error
        error = 4
        injector.override_injected_dependency(('data_manager',
                                               get_datamanager_mock))

        ret = flavor_logic.get_tags('some_id')

        self.assertEqual(ret, my_flavor.flavor.tag)

    def test_get_tags_not_found(self):
        global error
        error = 1
        injector.override_injected_dependency(('data_manager',
                                               get_datamanager_mock))

        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.get_tags,
                          'some_id')

    def test_get_tags_error(self):
        global error
        error = 2
        injector.override_injected_dependency(('data_manager',
                                               get_datamanager_mock))

        self.assertRaises(SystemError, flavor_logic.get_tags, 'some_id')

    def test_update_tags_success(self):
        global error
        error = 0
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))
        tag = TagsWrapper(tags={'a': 'b'})
        ret = flavor_logic.update_tags('some_id', tag, 'trans_id')

        self.assertEqual(ret.tags, tag.tags)

    def test_update_tags_not_found(self):
        global error
        error = 1
        injector.override_injected_dependency(('data_manager', get_datamanager_mock))

        self.assertRaises(NotFoundError, flavor_logic.update_tags, '', None, '')

    def test_update_tags_error(self):
        global error
        error = 2
        injector.override_injected_dependency(('data_manager', get_datamanager_mock))

        self.assertRaises(Exception, flavor_logic.update_tags, 'a', None, 'a')

    def test_delete_tags_success(self):
        tag = TagsWrapper(tags={'a': 'b'})
        flavor_logic.delete_tags('some_id', tag, 'trans_id')

    def test_delete_all_tags_success(self):
        flavor_logic.delete_tags('some_id', None, 'trans_id')

    def test_delete_tags_not_found(self):
        global error
        error = 6
        injector.override_injected_dependency(('data_manager', get_datamanager_mock))

        # Even when the tag was not found, an exception shouldn't be raised
        flavor_logic.delete_tags('some_id', None, 'trans_id')

        error = 7
        self.assertRaises(flavor_logic.NotFoundError, flavor_logic.delete_tags,
                          'some_id', None, 'trans_id')

        error = 8
        # This case should not raise an exception
        flavor_logic.delete_tags('some_id', None, 'trans_id')

    def test_delete_tags_error(self):
        global error
        error = 2
        injector.override_injected_dependency(('data_manager', get_datamanager_mock))

        self.assertRaises(Exception, flavor_logic.delete_tags, 'a', None, 'a')

        error = 9
        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.delete_tags,
                          'a', None, 'a')

    def test_delete_flavor_by_uuid_success(self):
        global error
        error = 31
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))

        flavor_logic.delete_flavor_by_uuid('some_id')

        error = 33
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))
        flavor_logic.delete_flavor_by_uuid('some_id')

    def test_delete_flavor_by_uuid_bad_status(self):
        global error
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))

        # Run once for response with no status and once for an invalid
        # response code
        for error_value in (32, 40,):
            error = error_value
            injector.override_injected_dependency(
                ('rds_proxy', get_rds_proxy_mock()))

            try:
                flavor_logic.delete_flavor_by_uuid('some_id')
                self.fail('ErrorStatus not raised!')
            except flavor_logic.ErrorStatus as e:
                self.assertEqual(e.status_code, 500)

        # RDS returned OK, but the resource status is Error
        error = 34
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))
        try:
            flavor_logic.delete_flavor_by_uuid('some_id')
            self.fail('ErrorStatus not raised!')
        except flavor_logic.ErrorStatus as e:
            self.assertEqual(e.status_code, 409)

    def test_delete_flavor_by_uuid_flavor_not_found(self):
        global error
        error = 1
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))

        flavor_logic.delete_flavor_by_uuid('some_id')

    def test_delete_flavor_by_uuid_flavor_has_regions(self):
        global error
        error = 3
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))

        try:
            flavor_logic.delete_flavor_by_uuid('some_id')
            self.fail('ErrorStatus not raised!')
        except flavor_logic.ErrorStatus as e:
            self.assertEqual(e.status_code, 405)

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_add_regions_success(self, mock_gfbu, mock_strin):
        ret_flavor = MagicMock()
        ret_flavor.flavor.regions = [Region(name='test_region')]
        mock_gfbu.return_value = ret_flavor
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))

        res_regions = flavor_logic.add_regions('uuid', RegionWrapper(
            [Region(name='test_region')]), 'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_add_regions_errors(self, mock_gfbu, mock_strin):
        ret_flavor = MagicMock()
        ret_flavor.flavor.regions = [Region(name='test_region')]
        mock_gfbu.return_value = ret_flavor
        global error

        error = 1
        injector.override_injected_dependency(('data_manager', get_datamanager_mock))
        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.add_regions,
                          'uuid', RegionWrapper([Region(name='test_region')]),
                          'transaction')

        error = 4
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))

        mock_strin.side_effect = flavor_logic.FlushError()
        self.assertRaises(flavor_logic.FlushError, flavor_logic.add_regions,
                          'uuid', RegionWrapper([Region(name='test_region')]),
                          'transaction')
        mock_strin.side_effect = flavor_logic.FlushError(
            'conflicts with persistent instance')
        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.add_regions,
                          'uuid', RegionWrapper([Region(name='test_region')]),
                          'transaction')
        mock_strin.side_effect = ValueError()
        self.assertRaises(ValueError, flavor_logic.add_regions,
                          'uuid', RegionWrapper([Region(name='test_region')]),
                          'transaction')
        mock_strin.side_effect = ValueError(
            'conflicts with persistent instance')
        self.assertRaises(flavor_logic.ConflictError, flavor_logic.add_regions,
                          'uuid', RegionWrapper([Region(name='test_region')]),
                          'transaction')

        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.add_regions,
                          'uuid', RegionWrapper([Region(name='')]),
                          'transaction')
        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.add_regions,
                          'uuid', RegionWrapper([Region(name='test_region', type='group')]),
                          'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_delete_region_success(self, mock_gfbu, mock_strin):
        ret_flavor = MagicMock()
        ret_flavor.flavor.regions = [Region(name='test_region')]
        mock_gfbu.return_value = ret_flavor
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))

        res_regions = flavor_logic.delete_region('uuid', RegionWrapper(
            [Region(name='test_region')]), 'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_delete_region_errors(self, mock_gfbu, mock_strin):
        ret_flavor = MagicMock()
        ret_flavor.flavor.regions = [Region(name='test_region')]
        mock_gfbu.return_value = ret_flavor
        global error

        error = 1
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))
        self.assertRaises(flavor_logic.ErrorStatus, flavor_logic.delete_region,
                          'uuid', 'test_region', 'transaction')

        error = 2
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))
        self.assertRaises(SystemError, flavor_logic.delete_region,
                          'uuid', 'test_region', 'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_add_tenants_success(self, mock_gfbu, mock_strin):
        ret_flavor = MagicMock()
        tenants = ['test_tenant']
        ret_flavor.flavor.tenants = tenants
        mock_gfbu.return_value = ret_flavor
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))

        res_tenants = flavor_logic.add_tenants('uuid',
                                               TenantWrapper(tenants),
                                               'transaction')
        self.assertEqual(res_tenants.tenants, tenants)

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_add_tenants_errors(self, mock_gfbu, mock_strin):
        ret_flavor = MagicMock()
        tenants = ['test_tenant']
        ret_flavor.flavor.tenants = tenants
        mock_gfbu.return_value = ret_flavor
        global error

        error = 1
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))
        self.assertRaises(flavor_logic.ErrorStatus,
                          flavor_logic.add_tenants, 'uuid',
                          TenantWrapper(tenants),
                          'transaction')

        # Flavor is public
        error = 5
        self.assertRaises(flavor_logic.ErrorStatus,
                          flavor_logic.add_tenants, 'uuid',
                          TenantWrapper(tenants),
                          'transaction')

        error = 31
        moq = MagicMock()
        moq.tenants = [1337]
        self.assertRaises(ValueError,
                          flavor_logic.add_tenants, 'uuid',
                          moq,
                          'transaction')

        mock_strin.side_effect = flavor_logic.FlushError(
            'conflicts with persistent instance')
        self.assertRaises(flavor_logic.ConflictError,
                          flavor_logic.add_tenants, 'uuid',
                          TenantWrapper(tenants),
                          'transaction')

        mock_strin.side_effect = flavor_logic.FlushError('')
        self.assertRaises(flavor_logic.FlushError,
                          flavor_logic.add_tenants, 'uuid',
                          TenantWrapper(tenants),
                          'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_delete_tenant_success(self, mock_gfbu, mock_strin):
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))

        flavor_logic.delete_tenant('uuid', 'tenant_id', 'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    def test_delete_tenant_errors(self, mock_gfbu, mock_strin):
        ret_flavor = MagicMock()
        tenants = ['test_tenant']
        ret_flavor.flavor.tenants = tenants
        mock_gfbu.return_value = ret_flavor
        global error

        error = 1
        injector.override_injected_dependency(
            ('data_manager', get_datamanager_mock))
        self.assertRaises(flavor_logic.ErrorStatus,
                          flavor_logic.delete_tenant, 'uuid',
                          'tenant_id',
                          'transaction')

        # Flavor is public
        error = 5
        self.assertRaises(ValueError,
                          flavor_logic.delete_tenant, 'uuid',
                          'tenant_id',
                          'transaction')

        global FLAVOR_MOCK
        tenant = MagicMock()
        tenant.tenant_id = 'tenant_id'
        FLAVOR_MOCK.flavor_tenants = [tenant]
        error = 6
        self.assertRaises(ValueError,
                          flavor_logic.delete_tenant, 'uuid',
                          'tenant_id',
                          'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    @patch.object(models, 'request')
    @patch.object(flavor_logic, 'ExtraSpecsWrapper')
    def test_add_extra_specs_success(self, mock_extra_specs_wrapper,
                                     mock_request, mock_gfbu, mock_strin):
        extra_specs = ExtraSpecsWrapper({'a': 'b'})
        mock_extra_specs_wrapper.from_db_model.return_value = extra_specs
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))
        res_extra_specs = flavor_logic.add_extra_specs('uuid',
                                                       extra_specs,
                                                       'transaction')
        self.assertEqual(res_extra_specs.os_extra_specs, {'a': 'b'})

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    @patch.object(models, 'request')
    @patch.object(flavor_logic, 'ExtraSpecsWrapper')
    def test_add_extra_specs_conflict_error(self, mock_extra_specs_wrapper,
                                            mock_request, mock_gfbu,
                                            mock_strin):
        mock_strin.side_effect = ValueError(
            'conflicts with persistent instance')
        extra_specs = ExtraSpecsWrapper({'a': 'b'})
        mock_extra_specs_wrapper.from_db_model.return_value = extra_specs
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))
        self.assertRaises(flavor_logic.ConflictError,
                          flavor_logic.add_extra_specs, 'uuid',
                          extra_specs,
                          'transaction')

    @patch.object(flavor_logic, 'send_to_rds_if_needed')
    @patch.object(flavor_logic, 'get_flavor_by_uuid')
    @patch.object(models, 'request')
    @patch.object(flavor_logic, 'ExtraSpecsWrapper')
    @patch.object(flavor_logic, 'FlavorWrapper')
    def test_update_extra_specs_success(self, mock_flavor_wrapper,
                                        mock_extra_specs_wrapper,
                                        mock_request, mock_gfbu, mock_strin):
        extra_specs = ExtraSpecsWrapper({'a': 'b'})
        mock_extra_specs_wrapper.from_db_model.return_value = extra_specs
        global error
        error = 31
        injector.override_injected_dependency(
            ('rds_proxy', get_rds_proxy_mock()))
        res_extra_specs = flavor_logic.update_extra_specs('uuid',
                                                          extra_specs,
                                                          'transaction')
        self.assertEqual(res_extra_specs.os_extra_specs, {'a': 'b'})


def get_datamanager_mock():
    def get_record(record_type):
        global error
        if record_type == 'flavor':
            record = MagicMock()
            db_model = db_models.Flavor()
            db_model.remove_tag = MagicMock()
            db_model.remove_all_tags = MagicMock()
            record.get_flavor_by_id.return_value = db_model

            if error == 1:
                record.get_flavor_by_id.return_value = None
            elif error == 2:
                record.get_flavor_by_id.side_effect = SystemError()
            elif error == 3:
                moq = MagicMock()
                moq.get_existing_region_names.return_value = ['region']
                record.get_flavor_by_id.return_value = moq
            elif error == 4:
                record.get_flavor_by_id.return_value = db_models.Flavor()
            elif error == 5:
                record.get_flavor_by_id.return_value = db_models.Flavor(
                    visibility='public')
            elif error == 6:
                record.get_flavor_by_id.return_value = FLAVOR_MOCK
            elif error == 7:
                record.get_flavor_by_id.side_effect = flavor_logic.NotFoundError()
            elif error == 8:
                record.get_flavor_by_id.side_effect = flavor_logic.ErrorStatus(
                    404)
            elif error == 9:
                record.get_flavor_by_id.side_effect = flavor_logic.ErrorStatus(
                    500)
            else:
                record.get_flavor_by_id.return_value = MagicMock()
            return record

    mock = MagicMock()
    mock.get_record = get_record

    return mock


def get_rds_proxy_mock():
    def get_status(resource_id):
        global error
        response = MagicMock()

        if error == 31:
            response.status_code = 200
            response.json.return_value = {'status': 'Success'}
        elif error == 32:
            response.status_code = 200
            response.json.return_value = {}
        elif error == 33:
            response.status_code = 404
        elif error == 34:
            response.status_code = 200
            response.json.return_value = {'status': 'Error'}
        else:
            response.status_code = 500

        return response

    mock = MagicMock()
    mock.get_status = get_status

    return mock


def get_flavor_mock():
    flavor_mock = FlavorWrapper()
    flavor_mock.flavor = Flavor(ram='1024', vcpus='1', series='ss', id='g')
    flavor_mock.flavor.profile = 'N1'

    return flavor_mock


rds_proxy_mock = MagicMock()
rds_proxy_mock.get_status.return_value = {
    "status": "pending",
    "regions": [
        {
            "region": "dla1",
            "timestamp": "1451599200",
            "ord-transaction-id": "0649c5be323f4792afbc1efdd480847d",
            "resource-id": "12fde398643acbed32f8097c98aec20",
            "ord-notifier-id": "",
            "status": "success",
            "error-code": "200",
            "error-msg": "OK"
        }
    ]
}

extra_specs_json = {
    "os_extra_specs": {
        "name357": "region_name1",
        "name4467": "2",
        "name66767": "222234556"
    }
}
