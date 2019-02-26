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

from ranger_tempest_plugin.tests.api import ims_base
from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions

CONF = config.CONF


class TestTempestIms(ims_base.ImsBaseOrmTest):

    @classmethod
    def setup_credentials(cls):
        super(TestTempestIms, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(TestTempestIms, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        # setup public image for tempest testing
        cls.image_params = cls._get_image_params(set_private=False)
        cls.public_image = cls._create_img_and_validate_creation_on_dcp_and_lcp(
            **cls.image_params)

        # setup private image for tempest testing
        cls.image_params = cls._get_image_params(set_enabled=False)
        cls.private_image = cls._create_img_and_validate_creation_on_dcp_and_lcp(
            **cls.image_params)

        super(TestTempestIms, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        cls._del_img_validate_deletion_on_dcp_and_lcp(cls.public_image['id'])
        cls._del_img_validate_deletion_on_dcp_and_lcp(cls.private_image['id'])
        super(TestTempestIms, cls).resource_cleanup()

    def _data_setup(self, post_body):
        image = self._create_img_and_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_img_validate_deletion_on_dcp_and_lcp,
                        image["id"])
        # only check for Success image status if "regions" is not empty
        if image["regions"]:
            self._wait_for_image_status_on_dcp(image["id"], 'Success')

        return image

    @decorators.idempotent_id('2b1bb28b-4151-4e75-ae1b-d21089c3418c')
    def test_get_image(self):
        """ Execute 'get_image' using the following options:
        -  get image by id   (using cust_id parameter)
        -  get image by name (using cust_name parameter)
        """

        # execute get_image using image ID  and iamge_name
        for identifier in [self.public_image['id'], self.public_image['name']]:
            _, body = self.client.get_image(identifier)
            self.assertIn(self.public_image['id'], body['image']['id'])

    @decorators.idempotent_id('6072c438-1e45-4c0b-97a6-e5127bd33d90')
    def test_list_images_with_filters(self):
        """ This function executes 'list customer' with all available filters:
        -  no filter  (i.e.  list all images)
        -  filter by region
        -  filter by customer
        """

        # define the list customer filters to be used for this test
        no_filter = None
        customer_filter = "?customer=%s" % self.tenant_id
        region_filter = "?region=%s" % self.region_id

        # execute list_customers with the available filters
        for list_filter in [no_filter, region_filter,
                            customer_filter]:
            # import pdb; pdb.set_trace()
            _, body = self.client.list_images(list_filter)
            images = [image['id'] for image in body['images']]
            self.assertIn(self.private_image['id'], images)

    @decorators.idempotent_id('eae7ca20-5383-4579-9f73-0138b8b3ec85')
    def test_list_image_visibility(self):
        """ List images with visibility = public/private
        """
        # list public images and check if self.public_image is in the list
        _, body = self.client.list_images()
        image_ids = [img['id'] for img in body['images']]
        self.assertIn(self.public_image['id'], image_ids)

        # list private images and check if self.private_image is in the list
        _, body = self.client.list_images()
        image_ids = [img['id'] for img in body['images']]
        self.assertIn(self.private_image['id'], image_ids)

    @decorators.idempotent_id('4435fef4-49a9-435b-8463-cf8a1e0b7cd8')
    def test_disable_image(self):
        # disable self.public_image and check if request is successful
        self.client.enabled_image(self.public_image['id'], False)
        self._wait_for_image_status_on_dcp(self.public_image['id'], 'Success')
        _, body = self.client.get_image(self.public_image['id'])
        image = body["image"]

        # assert that the image["enabled"] value is 'False'
        self.assertTrue(not image['enabled'])

    @decorators.idempotent_id('f32a13e3-6f38-423b-a616-09c8d4e1c277')
    def test_enable_image(self):
        # enable self.private_image and check if request is successful
        self.client.enabled_image(self.private_image['id'], True)
        self._wait_for_image_status_on_dcp(self.private_image['id'], 'Success')
        _, body = self.client.get_image(self.private_image['id'])
        image = body["image"]

        # assert that the image["enabled"] value is 'True'
        self.assertTrue(image['enabled'])

    @decorators.idempotent_id('cb9e3022-00d7-4a21-bdb2-67d3cd15a4f8')
    def test_add_delete_image_region(self):
        # skip region assignment in data setup
        post_body = self._get_image_params(set_region=False)
        image = self._data_setup(post_body)
        test_image_id = image['id']

        # add region to image then check to confirm image status = "Success"
        self.client.add_region_to_image(test_image_id, self.region_id)
        # image status must show 'Success' when assigned to a region
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')

        # check that region is successfully added
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertEqual(image["regions"][0]["name"], self.region_id)

        # delete the region then check to confirm image status = "no regions"
        _, body = self.client.delete_region_from_image(test_image_id,
                                                       self.region_id)
        self._wait_for_image_status_on_dcp(test_image_id, 'no regions')

        # image region array should be empty after the region was removed
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertFalse(image["regions"])

    @decorators.idempotent_id('0ee68189-66a8-4213-ad68-bc12991c174a')
    def test_add_delete_image_tenant(self):
        # add alt tenant to self.private_image and check if status = "Success"
        self.client.add_customer_to_image(self.private_image['id'], self.alt_tenant_id)
        self._wait_for_image_status_on_dcp(self.private_image['id'], 'Success')

        # check that alt tenant successfully added to image tenants array
        _, body = self.client.get_image(self.private_image['id'])
        image = body["image"]
        self.assertEqual(len(image["customers"]), 2)
        self.assertIn(self.alt_tenant_id, image['customers'])

        # now delete alt_tenant_id and ensure operation is successful
        _, body = self.client.delete_customer_from_image(self.private_image['id'],
                                                         self.alt_tenant_id)
        self._wait_for_image_status_on_dcp(self.private_image['id'], 'Success')

        # image region array should no longer contain alt tenant
        _, body = self.client.get_image(self.private_image['id'])
        image = body["image"]
        self.assertNotIn(self.alt_tenant_id, image['customers'])

    @decorators.idempotent_id('bac99348-6b13-4b30-958b-3c039b27eda3')
    def test_update_image_tenant(self):
        # replace current tenant in self.private_image with alt tenant
        self.client.update_customer(self.private_image['id'], self.alt_tenant_id)
        self._wait_for_image_status_on_dcp(self.private_image['id'], 'Success')

        # check that image tenants array contains only alt tenant
        _, body = self.client.get_image(self.private_image['id'])
        image = body["image"]
        self.assertEqual(len(image["customers"]), 1)
        self.assertIn(self.alt_tenant_id, image['customers'])

    @decorators.idempotent_id('0331e02a-ab52-4341-b676-a02462244277')
    def test_create_image(self):
        post_body = self._get_image_params()
        # call client create_IMAGE and wait till status equals 'Success'
        _, body = self.client.create_image(**post_body)
        image = body["image"]
        test_image_id = image["id"]
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')

        # do not forget to add this account to addCleanUp
        self.addCleanup(self._del_img_validate_deletion_on_dcp_and_lcp,
                        test_image_id)
        # verify image record created successfully
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertEqual(image["regions"][0]["name"], CONF.identity.region)

    @decorators.idempotent_id('01160918-e217-401d-a6a0-e7992ab76e41')
    def test_update_image(self):
        region = {}
        post_body = self._get_image_params(set_region=False,
                                           set_enabled=False)
        image = self._data_setup(post_body)
        test_image_id = image['id']

        # setup region and change 'enabled' and 'customer' properties
        region["name"] = self.region_id
        region["type"] = "single"
        region["checksum"] = "7297321c2fa6424417a548c85edd6e98"
        region["virtual_size"] = "None"
        region["size"] = "38797312"
        post_body["regions"] = [region]

        post_body["enabled"] = True
        post_body["customers"] = [self.alt_tenant_id]
        _, body = self.client.update_image(test_image_id, para=None,
                                           **post_body)
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')
        # verify image record updated successfully
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertEqual(image["regions"][0]["name"], CONF.identity.region)
        self.assertIn(self.alt_tenant_id, image['customers'])
        self.assertTrue(image['enabled'])

    @decorators.idempotent_id('23e2e7e2-5b19-4c66-b35c-7c686a986627')
    def test_delete_image(self):
        # setup data for test case
        post_body = self._get_image_params()
        image = self._create_img_and_validate_creation_on_dcp_and_lcp(
            **post_body)
        test_image_id = image['id']

        # delete the data and do get_image to ensure 404-NotFound response
        self._del_img_validate_deletion_on_dcp_and_lcp(test_image_id)
        self.assertRaises(exceptions.NotFound, self.client.get_image,
                          test_image_id)
