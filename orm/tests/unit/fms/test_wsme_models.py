from orm.services.flavor_manager.fms_rest.data.sql_alchemy import db_models
from orm.services.flavor_manager.fms_rest.data.wsme import models

from orm.tests.unit.fms import FunctionalTest
from oslo_config import cfg


class TestWsmeModels(FunctionalTest):
    def test_flavor_wrapper_from_db_model(self):

        sql_flavor = db_models.Flavor()
        sql_flavor.description = 'desc'
        sql_flavor.disk = 1
        sql_flavor.ephemeral = 1
        sql_flavor.flavor_extra_specs = [db_models.FlavorExtraSpec(
            'key1', 'val1'),
                                         db_models.FlavorExtraSpec(
            'key2', 'val2')]
        sql_flavor.flavor_tag = [db_models.FlavorExtraSpec('key1', 'val1'),
                                 db_models.FlavorExtraSpec('key2', 'val2')]
        sql_flavor.flavor_options = [db_models.FlavorExtraSpec('key1', 'val1'),
                                     db_models.FlavorExtraSpec('key2', 'val2')]
        sql_flavor.flavor_regions = [db_models.FlavorRegion('region1'),
                                     db_models.FlavorRegion('region2')]
        sql_flavor.flavor_tenants = [db_models.FlavorTenant('tenant1'),
                                     db_models.FlavorTenant('tenant2')]
        sql_flavor.id = 'id'
        sql_flavor.internal_id = 1
        sql_flavor.ram = 1
        sql_flavor.visibility = 'visibility'
        sql_flavor.vcpus = 1
        sql_flavor.series = cfg.CONF.fms.flavor_series[0]
        sql_flavor.swap = 1
        sql_flavor.disk = 1
        sql_flavor.name = 'name'

        wsme_flavors = models.FlavorWrapper.from_db_model(sql_flavor)

        self.assertEqual(len(wsme_flavors.flavor.regions), 2)
        self.assertEqual(len(wsme_flavors.flavor.tenants), 2)
        self.assertEqual(wsme_flavors.flavor.extra_specs['key1'], 'val1')
        self.assertEqual(wsme_flavors.flavor.extra_specs['key2'], 'val2')

    def test_flavor_wrapper_to_db_model(self):
        flavor_wrapper = models.FlavorWrapper()
        flavor_wrapper.flavor = models.Flavor()

        flavor_wrapper.flavor.description = 'desc'
        flavor_wrapper.flavor.disk = '1'
        flavor_wrapper.flavor.ephemeral = '1'
        flavor_wrapper.flavor.extra_specs = {'key1': 'val1', 'key2': 'val2'}
        flavor_wrapper.flavor.tag = {'key1': 'val1', 'key2': 'val2'}
        flavor_wrapper.flavor.options = {'key1': 'val1', 'key2': 'val2'}
        flavor_wrapper.flavor.regions = [models.Region('region1'),
                                         models.Region('region2')]
        flavor_wrapper.flavor.tenants = ['tenant1', 'tenant2']
        flavor_wrapper.flavor.id = 'id'
        flavor_wrapper.flavor.ram = '1'
        flavor_wrapper.flavor.visibility = 'visibility'
        flavor_wrapper.flavor.vcpus = '1'
        flavor_wrapper.flavor.swap = '1'
        flavor_wrapper.flavor.disk = '1'
        flavor_wrapper.flavor.name = 'name'
        flavor_wrapper.flavor.series = cfg.CONF.fms.flavor_series[0]

        sql_flavor = flavor_wrapper.to_db_model()

        self.assertEqual(len(sql_flavor.flavor_regions), 2)
        self.assertEqual(len(sql_flavor.flavor_tenants), 2)

        spec = next(
            s for s in sql_flavor.flavor_extra_specs if s.key_name == 'key1')
        self.assertEqual(spec.key_value, 'val1')

    def test_flavor_summary_from_db_model(self):
        sql_flavor = db_models.Flavor()
        sql_flavor.id = 'some id'
        sql_flavor.name = 'some name'
        sql_flavor.description = 'some_decription'

        flavor_summary = models.FlavorSummary.from_db_model(sql_flavor)

        self.assertEqual(flavor_summary.id, sql_flavor.id)
        self.assertEqual(flavor_summary.name, sql_flavor.name)
        self.assertEqual(flavor_summary.description, sql_flavor.description)
