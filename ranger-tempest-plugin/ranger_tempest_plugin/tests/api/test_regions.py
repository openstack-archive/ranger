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
from ranger_tempest_plugin.tests.api import rms_base

from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib import decorators

CONF = config.CONF


class TestTempestRegion(rms_base.RmsBaseOrmTest):

    @classmethod
    def resource_setup(cls):
        cls.setup_ids = []
        # create standard region
        _, cls.region_1 = cls.client.create_region(data_utils.rand_name())
        cls.setup_ids.append(cls.region_1['id'])
        # create region sharing region_1 properties
        _, cls.region_2 = cls.client.create_region(data_utils.rand_name())
        cls.setup_ids.append(cls.region_2['id'])
        # create region with differing properties
        _, cls.region_3 = cls.client.create_region(
            data_utils.rand_name(),
            **{'status': 'down',
                'rangerAgentVersion': '3.0',
                'OSVersion': 'mitaka',
                'CLLI': '123450',
                'address': {'country': 'Mexico', 'state': 'Sonora',
                            'city': 'Nogales', 'street': '12 main',
                            'zip': '84000'},
                'metadata': {'meta1': ['val1']},
                'designType': 'large'})
        cls.setup_ids.append(cls.region_3['id'])

        super(TestTempestRegion, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        for region_id in cls.setup_ids:
            cls.client.delete_region(region_id)
        super(TestTempestRegion, cls).resource_cleanup()

    @decorators.idempotent_id('eecedcb0-9c96-453d-bd72-71dba26fa1c5')
    def test_list_region(self):
        _, body = self.client.list_regions()
        regions = [x['id'] for x in body['regions']]
        self.assertIn(self.region_1['id'], regions)

    @decorators.idempotent_id('0164e040-7775-4837-9ac2-aaa0f71cdfca')
    def test_list_region_v1(self):
        _, body = self.client.list_regions_v1()
        regions = [x['id'] for x in body]
        self.assertIn(self.region_1['id'], regions)

    @decorators.idempotent_id('e6c6fdfe-5fa2-45f5-8bd8-fb9cf79e99fc')
    def test_list_region_with_name(self):
        filter = {'regionname': self.region_1['name']}
        self._list_regions_with_filter(filter, 'name')

    @decorators.idempotent_id('b3310e32-0c31-4d37-9789-cc3c4639dabe')
    def test_list_region_with_osversion(self):
        filter = {'osversion': self.region_1['OSVersion']}
        self._list_regions_with_filter(filter, 'OSVersion')

    @decorators.idempotent_id('0b2d3e79-c14a-4527-94b0-04eeae053a80')
    def test_list_region_with_status(self):
        filter = {'status': self.region_1['status']}
        self._list_regions_with_filter(filter, 'status')

    @decorators.idempotent_id('871be582-ecaa-4a46-a403-4d6b5e59d7de')
    def test_list_region_with_ranger_version(self):
        filter = {'ranger_agent_version': self.region_1['rangerAgentVersion']}
        self._list_regions_with_filter(filter, 'rangerAgentVersion')

    @decorators.idempotent_id('ac18be48-c787-4a65-913f-a0b0a80fbd1d')
    def test_list_region_with_clli(self):
        filter = {'clli': self.region_1['CLLI']}
        self._list_regions_with_filter(filter, 'CLLI')

    @decorators.idempotent_id('f2b2361d-ce71-43a8-9f01-acb529835880')
    def test_list_region_with_metadata(self):
        filter = {'metadata': self.region_1['metadata'].keys()[0]}
        self._list_regions_with_filter(filter, 'metadata')

    @decorators.idempotent_id('4533b31a-115d-466d-bf75-8ac24338c1a5')
    def test_list_region_with_address(self):
        filter = {
            'country': self.region_1['address']['country'],
            'city': self.region_1['address']['city'],
            'street': self.region_1['address']['street'],
            'zip': self.region_1['address']['zip']
        }
        self._list_regions_with_filter(filter, 'address')

    @decorators.idempotent_id('726b8215-af10-4385-83c7-32b51502dff1')
    def test_list_region_with_type(self):
        filter = {'type': self.region_1['designType']}
        self._list_regions_with_filter(filter, 'designType')

    @decorators.idempotent_id('4875ea70-a5a1-4b46-b752-246221670d26')
    def test_list_region_with_vlcp(self):
        filter = {'vlcp_name': self.region_1['vlcpName']}
        self._list_regions_with_filter(filter, 'vlcpName')

    @decorators.idempotent_id('77257e0c-e2f8-4b98-886c-359508a4a73d')
    def test_list_multiple_filter(self):
        filter = {
            'vlcp_name': self.region_1['vlcpName'],
            'status': self.region_1['status'],
            'regionname': self.region_1['name']
        }
        self._list_regions_with_filter(filter, 'name')

    @decorators.idempotent_id('358f3cbc-4ae5-4b43-be36-6df55eae8fd9')
    def test_get_region(self):
        _, body = self.client.get_region(self.region_1['id'])
        self.assertExpected(self.region_1, body, [])

    @decorators.idempotent_id('cefb952f-7777-4878-87d2-d78ac345f0d2')
    def test_get_region_metadata(self):
        _, body = self.client.get_region_metadata(self.region_1['id'])
        self.assertExpected(self.region_1['metadata'], body['metadata'], [])

    @decorators.idempotent_id('b2c3baf5-22af-4bf9-bcad-b6a1a74e82d9')
    def test_update_region(self):
        id = self.setup_ids[-1]
        region = orm_data_utils.rand_region(id)
        _, body = self.client.update_region(id, **region)
        self.assertExpected(region, body, [])

    @decorators.idempotent_id('0d5644d8-92bc-497c-8fc5-b57417d86e6d')
    def test_update_region_status(self):
        status = {}
        status['status'] = orm_data_utils.rand_region_status(
            [self.region_1['status']])
        _, body = self.client.update_region_status(self.region_1['id'], status)
        self.assertExpected(status, body, ['links'])

    @decorators.idempotent_id('5c1a2624-6abe-49e7-82c8-30e8df1377d0')
    def test_update_region_metadata(self):
        metadata = {}
        metadata['metadata'] = orm_data_utils.rand_region_metadata()
        _, body = self.client.update_region_metadata(self.region_1['id'],
                                                     metadata)
        self.assertExpected(metadata, body, [])

    def _list_regions_with_filter(self, filter, key):
        _, body = self.client.list_regions(filter)
        regions = [x for x in body['regions']]
        self.assertTrue(
            all([region[key] == self.region_1[key] for region in regions]))
