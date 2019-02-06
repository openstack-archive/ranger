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

from ranger_tempest_plugin.tests.api import cms_base
from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib import decorators
from tempest.lib import exceptions

CONF = config.CONF


class TestTempestCms(cms_base.CmsBaseOrmTest):

    @classmethod
    def resource_setup(cls):
        cls.setup_customer = cls._get_customer_params()
        cls.setup_customer_id = \
            cls._create_cust_validate_creation_on_dcp_and_lcp(
                **cls.setup_customer)

        cls.bare_customer = cls._get_bare_customer_params()
        cls.bare_customer_id = \
            cls._create_cust_validate_creation_on_dcp_and_lcp(
                **cls.bare_customer)

        super(TestTempestCms, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        cls._del_cust_validate_deletion_on_dcp_and_lcp(cls.setup_customer_id)
        cls._del_cust_validate_deletion_on_dcp_and_lcp(cls.bare_customer_id)
        super(TestTempestCms, cls).resource_cleanup()

    @decorators.idempotent_id('6072c438-1e45-4c0b-97a6-e5127bd33d89')
    def test_get_customer(self):
        """ Execute 'get_customer' using the following options:
        -  get customer by id   (using cust_id parameter)
        -  get customer by name (using cust_name parameter)
        """

        # execute get_customer using cust_id and cust_name
        for identifier in [self.setup_customer_id,
                           self.setup_customer['name']]:
            _, body = self.client.get_customer(identifier)
            self.assertIn(self.setup_customer_id, body['uuid'])

    @decorators.idempotent_id('6072c438-1e45-4c0b-97a6-e5127bd33d90')
    def test_list_customers_with_filters(self):
        """ This function executes 'list customer' with all available filters:
        -  no filter  (i.e.  list all customers)
        -  filter by metadata key
        -  filter by region
        -  filter by default user id
        -  customer name contains a substring
        -  customer name starting with a string
        """

        # format filter parameter values
        region_name = [
            region['name'] for region in self.setup_customer['regions']]
        userid = [user['id'] for user in self.setup_customer['users']]
        cust_name = self.setup_customer['name']
        substr_name = random.randint(0, len(cust_name))

        # get the first key from metadata as the metadata key filter
        metadata_key = list(self.setup_customer['metadata'].keys())[0]

        # define the list customer filters to be used for this test
        no_filter = None
        metadata_filter = {'metadata': metadata_key}
        region_filter = {'region': region_name[0]}
        user_filter = {'user': userid[0]}
        contains_filter = {'contains': cust_name[substr_name:]}
        startswith_filter = {'starts_with': cust_name[:substr_name]}

        # execute list_customers with the available filters
        for list_filter in [no_filter, metadata_filter, region_filter,
                            user_filter, contains_filter, startswith_filter]:
            _, body = self.client.list_customers(list_filter)
            customers = [cust['id'] for cust in body['customers']]
            self.assertIn(self.setup_customer_id, customers)

    @decorators.idempotent_id('ac132678-fdb6-4037-a310-813313044055')
    def test_enable_customer(self):
        # setup data for test case
        post_body = self._get_customer_params(enabled=False)
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)

        # update enabled status from 'False' to 'True' and validate update OK
        _, body = self.client.get_customer(test_customer_id)
        self.assertFalse(body['enabled'])
        self.client.enable_customer(test_customer_id, True)
        self._wait_for_status(test_customer_id, 'Success')
        _, body = self.client.get_customer(test_customer_id)
        self.assertTrue(body['enabled'])

    @decorators.idempotent_id('7dfd5f7e-7031-4ee1-b355-cd5cdeb21bd1')
    def test_add_default_user(self):
        # setup data for "add_default_user" test case; leave default
        # and region users blank at the initial data creation
        post_body = self._get_customer_params(default_users=False,
                                              region_users=False)
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)
        _, body = self.client.get_customer(test_customer_id)
        self.assertFalse(body['users'])
        self.assertFalse(body["regions"][0]['users'])

        # now add a default user, then validate that new user is added to
        # BOTH default user AND region user successfully
        post_default_user = self._get_user_params()
        new_user_id = post_default_user[0]["id"]
        _, body = self.client.add_default_user(test_customer_id,
                                               *post_default_user)
        self._wait_for_status(test_customer_id, 'Success')
        _, body = self.client.get_customer(test_customer_id)
        self.assertIn(new_user_id, [x['id'] for x in body['users']])
        self.assertIn(new_user_id, [x['id']
                      for x in body['regions'][0]['users']])

    @decorators.idempotent_id('699e8487-035e-4ae0-97b4-ca51b9a08aea')
    def test_delete_default_user(self):
        # setup data for delete_default_user test case
        post_body = self._get_customer_params()
        default_user_id = post_body["users"][0]["id"]
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)
        _, body = self.client.get_customer(test_customer_id)
        self.assertEqual(default_user_id, body['users'][0]['id'])
        self.assertIn(default_user_id,
                      [x['id'] for x in body['regions'][0]['users']])

        # delete default user and validate operation success by confirming
        # user id no longer in both default users and region users list
        _, body = self.client.delete_default_user(test_customer_id,
                                                  default_user_id)
        self._wait_for_status(test_customer_id, 'Success')
        _, body = self.client.get_customer(test_customer_id)
        self.assertFalse(body['users'])
        self.assertNotIn(default_user_id,
                         [x['id'] for x in body['regions'][0]['users']])

    @decorators.idempotent_id('48ffd49f-2b36-40b4-b1b4-0c805b7ba7c2')
    def test_replace_default_user(self):
        # setup data for "replace_default_user" test case; no need to
        # set region user as default user will also be assigned to it
        post_body = self._get_customer_params(region_users=False)
        default_user_id = post_body["users"][0]["id"]
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)
        _, body = self.client.get_customer(test_customer_id)
        self.assertIn(default_user_id, [x['id'] for x in body['users']])
        self.assertEqual(body['users'], body['regions'][0]['users'])

        # replace default user
        put_default_user = self._get_user_params(alt=True)
        updated_user_id = put_default_user[0]["id"]
        _, body = self.client.replace_default_user(test_customer_id,
                                                   *put_default_user)
        self._wait_for_status(test_customer_id, 'Success')

        # validate that BOTH the customer default user and region user
        # are replaced with the new default_user successfully
        _, body = self.client.get_customer(test_customer_id)
        self.assertEqual(len(body['users']),
                         len(body['regions'][0]['users']))
        self.assertIn(updated_user_id, [x['id'] for x in body['users']])
        self.assertEqual(body['users'], body['regions'][0]['users'])

    @decorators.idempotent_id('07a631f9-3aa5-4797-9ead-4531ced89e2a')
    def test_add_region_user(self):
        # We are leaving both default and region users as blank to ensure
        # region user is empty on initial data creation for this test case
        post_body = self._get_customer_params(region_users=False,
                                              default_users=False)
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)
        _, body = self.client.get_customer(test_customer_id)
        # confirm that the region users body is empty after data creation
        self.assertFalse(body["regions"][0]["users"])

        # now we shall add user to regions[0]
        post_region_user = self._get_user_params()
        _, body = self.client.add_region_user(test_customer_id,
                                              CONF.identity.region,
                                              *post_region_user)
        self._wait_for_status(test_customer_id, 'Success')
        _, customer = self.client.get_customer(test_customer_id)
        # validate that the region user is no longer empty after the add
        self.assertTrue(customer["regions"][0]["users"])

    @decorators.idempotent_id('9b2b3af8-2444-4143-a9e6-78c33b36c823')
    def test_delete_region_user(self):
        # To test delete_region_users scenario, leave default user blank
        # for the test customer data,  or else default user info will be
        # added as region user as well
        post_body = self._get_customer_params(default_users=False)
        region_user_id = post_body["regions"][0]["users"][0]["id"]
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)
        _, body = self.client.get_customer(test_customer_id)
        self.assertTrue(body["regions"][0]["users"])

        # delete the user from the region, then validate operation success
        _, body = self.client.delete_region_user(test_customer_id,
                                                 CONF.identity.region,
                                                 region_user_id)
        self._wait_for_status(test_customer_id, 'Success')
        _, customer = self.client.get_customer(test_customer_id)
        # validate that the region user is now empty
        self.assertFalse(customer["regions"][0]["users"])

    @decorators.idempotent_id('0ca59977-ef29-46b9-be92-14980a12c573')
    def test_replace_region_user(self):
        post_body = self._get_customer_params()
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)

        # update region user then confirm that update is successful
        put_region_user = self._get_user_params(alt=True)
        new_region_user_id = put_region_user[0]["id"]

        _, body = self.client.replace_region_user(test_customer_id,
                                                  CONF.identity.region,
                                                  *put_region_user)
        self._wait_for_status(test_customer_id, 'Success')
        _, customer = self.client.get_customer(test_customer_id)
        self.assertIn(new_region_user_id, [x['id']
                      for x in customer["regions"][0]['users']])

    @decorators.idempotent_id('f1444965-c711-438d-ab86-a2412acbe8e0')
    def test_replace_metadata(self):
        metadata = {'metadata': {'replace_key': 'replace_value'}}
        _, body = self.client.replace_metadata(self.setup_customer_id,
                                               metadata)
        self._wait_for_status(self.setup_customer_id, 'Success')
        _, body = self.client.list_customers({'metadata': 'replace_key'})
        self.assertIn(self.setup_customer_id,
                      [x['id'] for x in body['customers']])

    @decorators.idempotent_id('80713a87-8e95-481f-a198-6b4515d48362')
    def test_add_metadata(self):
        metadata = {'metadata': {'add_key': 'add_value'}}
        _, body = self.client.add_metadata(self.setup_customer_id,
                                           metadata)
        self._wait_for_status(self.setup_customer_id, 'Success')
        _, body = self.client.list_customers({'metadata': 'add_key'})
        self.assertIn(self.setup_customer_id,
                      [x['id'] for x in body['customers']])

    @decorators.idempotent_id('19a6bbe2-92b9-46be-95b7-aa0d9f247d88')
    def test_add_regions(self):
        region = self._get_region_params()
        _, body = self.client.add_regions(self.bare_customer_id,
                                          region)
        self._wait_for_status(self.setup_customer_id, 'Success')
        _, body = self.client.list_customers({'region': region[0]['name']})
        self.assertIn(self.setup_customer_id,
                      [x['id'] for x in body['customers']])

    @decorators.idempotent_id('09a43bc1-439e-4497-a026-f2c3de451d29')
    def test_delete_regions(self):
        # setup data for delete_region
        post_body = self._get_customer_params()
        region_name = post_body["regions"][0]["name"]
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)
        _, customer = self.client.get_customer(test_customer_id)
        self.assertTrue(customer["regions"])
        _, body = self.client.delete_region_from_customer(test_customer_id,
                                                          region_name)
        self._wait_for_status(test_customer_id, 'no regions')
        _, customer = self.client.get_customer(test_customer_id)
        self.assertFalse(customer["regions"])

    @decorators.idempotent_id('c7a24667-2a99-41ac-a42d-6c1163ef48af')
    def test_create_customer(self):
        post_body = self._get_customer_params(quota=False)
        test_cust_name = post_body['name']
        _, body = self.client.create_customer(**post_body)
        test_customer_id = body['customer']['id']
        self.addCleanup(self._del_cust_validate_deletion_on_dcp_and_lcp,
                        test_customer_id)
        self._wait_for_status(test_customer_id, 'Success')
        _, body = self.client.get_customer(test_cust_name)
        self.assertIn(test_customer_id, body['uuid'])

    @decorators.idempotent_id('43785f87-27d5-408d-997f-de602caeb698')
    def test_replace_customer(self):
        customer = self._get_bare_customer_params()
        customer['name'] = self.setup_customer['name']
        customer['regions'] = [{'name': CONF.identity.region}]
        _, body = self.client.update_customer(self.setup_customer_id,
                                              customer)
        self._wait_for_status(self.setup_customer_id, 'Success')
        _, body = self.client.get_customer(self.setup_customer_id)
        self.assertExpected(customer, body, ['name', 'regions'])
        for region in customer['regions']:
            self.assertIn(region['name'], [x['name'] for x in body['regions']])

    @decorators.idempotent_id('e8b9077a-d45c-4e24-a433-e7dfa07486b9')
    def test_delete_customer(self):
        # setup data for test case
        post_body = self._get_customer_params()
        test_customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **post_body)

        # delete the data and do get_customer to ensure 404-NotFound response
        self._del_cust_validate_deletion_on_dcp_and_lcp(test_customer_id)
        self.assertRaises(exceptions.NotFound, self.client.get_customer,
                          test_customer_id)

    @decorators.idempotent_id('b8493b3f-e64d-448e-a965-b0eeff415981')
    def test_customer_while_region_down(self):
        # create region with status down
        _, region = self.client.create_region(
            **{
                'name': data_utils.rand_name(),
                'status': 'down',
            }
        )

        # create customer within that newly created region
        cust_body = self._get_customer_params()
        cust_body['region'] = [region]
        customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **cust_body
        )
        _, body = self.client.get_customer(customer_id)
        # assert status show error
        self.assertEqual(customer_id, body['id'])
        self.assertEqual(body['status'], 'Error')

    @decorators.idempotent_id('1aa52c36-4b1e-459e-9633-12b6cbd53ae7')
    def test_customer_while_region_building(self):
        # create region with status building
        _, region = self.client.create_region(
            **{
                'name': data_utils.rand_name(),
                'status': 'building',
            }
        )

        # create customer within that newly created region
        cust_body = self._get_customer_params()
        cust_body['region'] = [region]
        customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **cust_body
        )
        _, body = self.client.get_customer(customer_id)
        # assert status
        self.assertEqual(customer_id, body['id'])
        self.assertEqual(body['status'], 'Success')

    @decorators.idempotent_id('d3cd949e-7895-421c-aeee-2c3d862c391f')
    def test_customer_while_region_maintenance(self):
        # create region with status maintenance
        _, region = self.client.create_region(
            **{
                'name': data_utils.rand_name(),
                'status': 'maintenance',
            }
        )

        # create customer within that newly created region
        cust_body = self._get_customer_params()
        cust_body['region'] = [region]
        customer_id = self._create_cust_validate_creation_on_dcp_and_lcp(
            **cust_body
        )
        _, body = self.client.get_customer(customer_id)
        # assert status
        self.assertEqual(customer_id, body['id'])
        self.assertEqual(body['status'], 'Success')
