# Copyright 2016 AT&T Corp
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the 'License'); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import random

from ranger_tempest_plugin.tests.api import grp_base
from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions

CONF = config.CONF


class TestTempestGrp(grp_base.GrpBaseOrmTest):

    @classmethod
    def resource_setup(cls):
        cls.setup_group = cls._get_group_params()
        cls.setup_group_id = \
            cls._create_grp_validate_creation_on_dcp_and_lcp(
                **cls.setup_group)
        super(TestTempestGrp, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        cls._del_group_validate_deletion_on_dcp_and_lcp(cls.setup_group_id)
        super(TestTempestGrp, cls).resource_cleanup()

    @decorators.idempotent_id('deeb3b8a-fb38-46e1-97ba-c878b0ba890f')
    def test_get_group(self):
        """ Execute 'get_group' using the following options:
        -  get group by id   
        -  get group by name 
        """

        # execute get_group using group id and group name
        for identifier in [self.setup_group_id,
                           self.setup_group['name']]:
            _, body = self.client.get_group(identifier)
            self.assertIn(self.setup_group_id, body['uuid'])

    @decorators.idempotent_id('8068e33f-a6aa-416a-9505-048c6ad037b2')
    def test_list_groups_with_filters(self):
        """ This function executes 'list groups' with all available filters:
        -  no filter  (i.e.  list all groups)
        -  filter by region
        -  group name contains a substring
        -  group name starts_with a string
        """

        # format filter parameter values
        region_name = [
            region['name'] for region in self.setup_group['regions']]
        group_name = self.setup_group['name']
        substr_name = random.randint(0, len(group_name))

        # define the list groups filters to be used for this test
        no_filter = None
        region_filter = {'region': region_name[0]}
        contains_filter = {'contains': group_name[substr_name:]}
        startswith_filter = {'starts_with': group_name[:substr_name]}

        # execute list_groups with the available filters
        for list_filter in [no_filter, region_filter, contains_filter,
                            startswith_filter]:
            _, body = self.client.list_groups(list_filter)
            groups = [grp['id'] for grp in body['groups']]
            self.assertIn(self.setup_group_id, groups)

    @decorators.idempotent_id('880f614f-6317-4973-a244-f2e44443f551')
    def test_delete_regions(self):
        # setup data for delete_region
        post_body = self._get_group_params()
        region_name = post_body["regions"][0]["name"]
        test_group_id = self._create_grp_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_group_validate_deletion_on_dcp_and_lcp,
                        test_group_id)
        _, group = self.client.get_group(test_group_id)
        self.assertTrue(group["regions"])
        _, body = self.client.delete_region_from_group(test_group_id,
                                                          region_name)
        self._wait_for_group_status(test_group_id, 'no regions')
        _, group = self.client.get_group(test_group_id)
        self.assertFalse(group["regions"])

    @decorators.idempotent_id('bba25028-d962-47df-9566-557eec48f22d')
    def test_create_group(self):
        post_body = self._get_group_params()
        test_group_name = post_body['name']
        _, body = self.client.create_group(**post_body)
        test_group_id = body['group']['id']
        self.addCleanup(self._del_group_validate_deletion_on_dcp_and_lcp,
                        test_group_id)
        self._wait_for_group_status(test_group_id, 'Success')
        _, body = self.client.get_group(test_group_name)
        self.assertIn(test_group_id, body['uuid'])

    @decorators.idempotent_id('356633f0-c615-4bdc-8f0f-d97b6ca409e0')
    def test_delete_group(self):
        # setup data for test case
        post_body = self._get_group_params()
        test_group_id = self._create_grp_validate_creation_on_dcp_and_lcp(
            **post_body)

        # delete the data and do get_group to ensure 404-NotFound response
        self._del_group_validate_deletion_on_dcp_and_lcp(test_group_id)
        self.assertRaises(exceptions.NotFound, self.client.get_group,
                          test_group_id)
