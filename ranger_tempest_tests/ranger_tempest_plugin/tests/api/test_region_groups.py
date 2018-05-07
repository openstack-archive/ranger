# Copyright 2016 AT&T Corp
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from ranger_tempest_plugin import data_utils as orm_data_utils
from ranger_tempest_plugin.tests.api import base

from tempest import config
from tempest.lib import decorators
from tempest.lib.common.utils import data_utils

CONF = config.CONF


class TestTempestRegionGroup(base.BaseOrmTest):

    @classmethod
    def setup_credentials(cls):
        super(TestTempestRegionGroup, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(TestTempestRegionGroup, cls).setup_clients()
        cls.client = cls.os_primary.rms_client

    @classmethod
    def resource_setup(cls):
        cls.setup_ids = []
        cls.group_ids = []
        # create standard region
        _, cls.region_1 = cls.client.create_region(data_utils.rand_name())
        cls.setup_ids.append(cls.region_1['id'])
        # create region sharing region_1 properties
        _, cls.region_2 = cls.client.create_region(data_utils.rand_name())
        cls.setup_ids.append(cls.region_2['id'])

        _, cls.group_1 = cls.client.create_region_group(
            **orm_data_utils.rand_region_group([cls.setup_ids[0]])
            )
        cls.group_ids.append(cls.group_1['group']['id'])
        _, cls.group_2 = cls.client.create_region_group(
            **orm_data_utils.rand_region_group(cls.setup_ids)
            )
        cls.group_ids.append(cls.group_2['group']['id'])

        super(TestTempestRegionGroup, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        for region_id in cls.setup_ids:
            cls.client.delete_region(region_id)
        for group_id in cls.group_ids:
            cls.client.delete_region_group(group_id)
        super(TestTempestRegionGroup, cls).resource_cleanup()

    @decorators.idempotent_id('0d377eb2-754d-49c1-9a4f-c7019dfe80ca')
    def test_update_group(self):
        id = self.group_ids[-1]
        group = orm_data_utils.rand_region_group(self.setup_ids, id)
        _, body = self.client.update_region_group(id, **group)
        self.assertExpected(group, body['group'], ['regions'])

    @decorators.idempotent_id('b946c6c4-d601-42b9-befd-ba40992a3c53')
    def test_list_groups(self):
        _, body = self.client.list_region_groups()
        groups = [x['id'] for x in body['groups']]
        self.assertIn(self.group_1['group']['id'], groups)
        self.assertIn(self.group_2['group']['id'], groups)

    @decorators.idempotent_id('9a37d966-4416-4ff3-8f3b-6847810662d7')
    def test_get_group(self):
        id = self.group_1['group']['id']
        _, body = self.client.get_region_group(id)
        self.assertExpected(self.group_1['group'], body, ['links'])
