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
        # create an image for tempest testing
        cls.image_params = cls._get_image_params()
        cls.image = cls._create_img_and_validate_creation_on_dcp_and_lcp(
            **cls.image_params)

        # save off specific data needed for our tempest tests
        cls.image_id = cls.image['id']
        cls.image_name = cls.image['name']
        # cls.visibility = cls.image['visibility']
        # cls.tenant_id = cls.image["customers"][0]
        super(TestTempestIms, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        cls._del_img_validate_deletion_on_dcp_and_lcp(cls.image_id)
        #                                             cls.region_id)
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
        '''
            Execute 'get_image' using the following options:
            -  get image by id   (using cust_id parameter)
            -  get image by name (using cust_name parameter)
        '''
        # execute get_image using image ID  and iamge_name
        for identifier in [self.image_id, self.image_name]:
            _, body = self.client.get_image(identifier)
            self.assertIn(self.image_id, body['image']['id'])

    @decorators.idempotent_id('6072c438-1e45-4c0b-97a6-e5127bd33d90')
    def test_list_images_with_filters(self):
        '''
            this function executes 'list customer' with all available filters:
            -  no filter  (i.e.  list all images)
            -  filter by region
            -  filter by customer
        '''

        # define the list customer filters to be used for this test
        no_filter = None
        customer_filter = "?customer=%s" % self.tenant_id
        region_filter = "?region=%s" % self.region_id

        # execute list_customers with the available filters
        for list_filter in [no_filter, region_filter,
                            customer_filter]:
            _, body = self.client.list_images(list_filter)
            images = [image['id'] for image in body['images']]
            self.assertIn(self.image_id, images)

    @decorators.idempotent_id('eae7ca20-5383-4579-9f73-0138b8b3ec85')
    def test_list_public_images(self):
        '''
            list images with visibility = 'public'
        '''
        # set_private = False to create image with visibility = 'public'
        post_body = self._get_image_params(set_private=False)
        image = self._data_setup(post_body)
        test_image_id = image['id']
        # confirm image visibility is set to "public" after image is created
        self.assertEqual(image["visibility"], "public")
        filter_public_images = "?visibility=%s" % image["visibility"]

        # list all public images and check if test_image_id is in the list
        _, body = self.client.list_images(filter_public_images)
        image_ids = [img['id'] for img in body['images']]
        self.assertIn(test_image_id, image_ids)

    @decorators.idempotent_id('dc321d60-f3bd-477c-b7bf-1594626f0a12')
    def test_list_private_images(self):
        '''
            list images with visibility = 'private'
        '''
        # image data created with visibility = private set by default
        post_body = self._get_image_params()
        image = self._data_setup(post_body)
        test_image_id = image['id']
        # confirm image visibility is set to "private" after image is created
        self.assertEqual(image["visibility"], "private")
        filter_private_images = "?visibility=%s" % image["visibility"]

        # list all public images and check if test_image_id is in the list
        _, body = self.client.list_images(filter_private_images)
        image_ids = [img['id'] for img in body['images']]
        self.assertIn(test_image_id, image_ids)

    @decorators.idempotent_id('4435fef4-49a9-435b-8463-cf8a1e0b7cd8')
    def test_disable_image(self):
        # setup data for test case - "enabled" is set to "true" by default
        post_body = self._get_image_params()
        image = self._data_setup(post_body)
        test_image_id = image['id']
        # send False to IMS client enable_image function to disable customer
        self.client.enabled_image(test_image_id, False)
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        # assert that the image["enabled"] value is 'False'
        self.assertTrue(not image['enabled'])

    @decorators.idempotent_id('f32a13e3-6f38-423b-a616-09c8d4e1c277')
    def test_enable_image(self):
        # setup data for test case - set_enabled is set to "False"
        post_body = self._get_image_params(set_enabled=False)
        image = self._data_setup(post_body)
        test_image_id = image['id']
        # send True to IMS client enable_image function to enable customer
        self.client.enabled_image(test_image_id, True)
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        # assert that the image["enabled"] value is 'True'
        self.assertTrue(image['enabled'])

    @decorators.idempotent_id('cb9e3022-00d7-4a21-bdb2-67d3cd15a4f8')
    def test_add_image_region(self):
        # set_region = False to skip region assignment in data setup
        post_body = self._get_image_params(set_region=False)
        image = self._data_setup(post_body)
        test_image_id = image['id']

        # add region to image then check to confirm image status = "Success"
        self.client.add_region_to_image(test_image_id, self.region_id)
        # image status must show 'Success' when assigned to a region
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')
        # check that image regions array is populated correctly
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertEqual(image["regions"][0]["name"], self.region_id)

    @decorators.idempotent_id('1be2d6fd-57b0-4acf-b895-1996f857739b')
    def test_delete_image_region(self):
        # setup data for test case
        post_body = self._get_image_params()
        image = self._data_setup(post_body)
        test_image_id = image['id']

        # delete the region then check to confirm image status = "no regions"
        _, body = self.client.delete_region_from_image(test_image_id,
                                                       self.region_id)
        # image status must show 'no regions' when it has no region assigned
        self._wait_for_image_status_on_dcp(test_image_id, 'no regions')
        # image region array should be empty after the region was removed
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertFalse(image["regions"])

    @decorators.idempotent_id('0ee68189-66a8-4213-ad68-bc12991c174a')
    def test_add_image_tenant(self):
        post_body = self._get_image_params()
        image = self._data_setup(post_body)
        test_image_id = image['id']
        _, body = self.client.get_image(test_image_id)
        self.assertNotIn(self.alt_tenant_id, body['image']['customers'])

        # add another tenant to image then check if image status = "Success"
        self.client.add_customer_to_image(test_image_id, self.alt_tenant_id)
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')
        # check that image tenants array is populated correctly
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertEqual(len(image["customers"]), 2)
        self.assertIn(self.alt_tenant_id, body['image']['customers'])

    @decorators.idempotent_id('bac99348-6b13-4b30-958b-3c039b27eda3')
    def test_update_image_tenant(self):
        post_body = self._get_image_params()
        image = self._data_setup(post_body)
        test_image_id = image['id']
        _, body = self.client.get_image(test_image_id)
        self.assertNotIn(self.alt_tenant_id, body['image']['customers'])

        # add another tenant to image then check if image status = "Success"
        self.client.update_customer(test_image_id, self.alt_tenant_id)
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')
        # check that image tenants array is populated correctly
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertEqual(len(image["customers"]), 1)
        self.assertIn(self.alt_tenant_id, body['image']['customers'])

    @decorators.idempotent_id('0506f23d-2d30-4214-9a4a-003ace86aa7d')
    def test_delete_image_tenant(self):
        # assign two tenants to image
        post_body = self._get_image_params(single_tenant=False)
        image = self._data_setup(post_body)
        test_image_id = image['id']
        _, body = self.client.get_image(test_image_id)
        self.assertIn(self.alt_tenant_id, body['image']['customers'])

        # delete one tenant then check if image status = "Success"
        _, body = self.client.delete_customer_from_image(test_image_id,
                                                         self.alt_tenant_id)
        self._wait_for_image_status_on_dcp(test_image_id, 'Success')
        # image region array should be empty after the region was removed
        _, body = self.client.get_image(test_image_id)
        image = body["image"]
        self.assertNotIn(self.alt_tenant_id, body['image']['customers'])

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
        self.assertIn(self.alt_tenant_id, body['image']['customers'])
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
