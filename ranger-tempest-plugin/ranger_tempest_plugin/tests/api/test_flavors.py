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

import json

from ranger_tempest_plugin.tests.api import fms_base
from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib import decorators
from tempest.lib import exceptions

import uuid

CONF = config.CONF


class TestTempestFms(fms_base.FmsBaseOrmTest):

    @classmethod
    def setup_credentials(cls):
        super(TestTempestFms, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(TestTempestFms, cls).setup_clients()
        cls.rms_client = cls.os_primary.rms_client

    @classmethod
    def resource_setup(cls):

        # create flavor then save off flavor_id for use in test cases
        body = cls._get_flavor_params()
        cls.flavor = cls._create_flv_and_validate_creation_on_dcp_and_lcp(
            **body)

        # these variables will be used to test list filters
        cls.flavor_id = cls.flavor['id']
        cls.flavor_name = cls.flavor['name']
        cls.visibility = cls.flavor['visibility']
        cls.series = cls.flavor['series']
        cls.tenant_id = cls.tenant_id
        cls.region_id = CONF.identity.region
        cls.alias = cls.flavor['alias']
        cls.dflt_ex_specs = cls.flavor['extra-specs']
        super(TestTempestFms, cls).resource_setup()

    def _get_flavor_details(self, flavor_id):
        _, body = self.client.get_flavor(flavor_id)
        flavor = body["flavor"]
        return flavor

    def _data_setup(self, post_body):
        flavor = self._create_flv_and_validate_creation_on_dcp_and_lcp(
            **post_body)
        self.addCleanup(self._del_flv_and_validate_deletion_on_dcp_and_lcp,
                        flavor["id"])
        return flavor

    def _exec_tags_function(self, flavor_id, req_json, action, para):

        if action == 'add':
            _, body = self.client.add_tags(flavor_id, req_json)

        elif action == 'update':
            _, body = self.client.update_tags(flavor_id, req_json)

        elif action == 'delete':
            _, body = self.client.delete_tags(flavor_id, para)

        self._wait_for_flavor_status_on_dcp(flavor_id, 'Success')

    def _exec_ex_spec_function(self, flavor_id, es_body, action, para):
        if action == 'add':
            _, body = self.client.add_extra_specs(flavor_id, es_body)

        elif action == 'update':
            _, body = self.client.update_extra_specs(flavor_id, es_body)

        elif action == 'delete':
            _, body = self.client.delete_extra_specs(flavor_id, para)

        self._wait_for_flavor_status_on_dcp(flavor_id, 'Success')

    @classmethod
    def resource_cleanup(cls):
        # cls.delete_role_to_admin()
        flavor_id = cls.flavor['id']
        cls._del_flv_and_validate_deletion_on_dcp_and_lcp(flavor_id)
        super(TestTempestFms, cls).resource_cleanup()

    @decorators.idempotent_id('2a4481cd-acce-4a5d-af7c-940222a6238b')
    def test_get_flavor(self):
        """ Execute get_flavor using flavor_id / flavor_name
        """
        for para in [self.flavor_id, self.flavor_name]:
            _, body = self.client.get_flavor(para)
            self.assertIn(self.flavor_id, body["flavor"]["id"])

    @decorators.idempotent_id('c46a503a-951c-4d00-afaa-46076b54db16')
    def test_list_flavor_with_filters(self):
        """ This function executes 'list flavors' with the following filters:
        - None                 (no filters, i.e. list all flavors)
        - alias filter
        - region filter
        - visibility filter
        - 'contains' filter
        - 'starts_with' filter
        - 'series' filter
        - "tenant" filter
        """
        # for use by the 'constains and 'starts_with' filter
        str_index1 = data_utils.rand_int_id(0, len(self.flavor_name) - 1)
        str_index2 = data_utils.rand_int_id(str_index1 + 1,
                                            len(self.flavor_name))

        # define the list flavors filters to be used for this test
        alias_filter = "?alias=%s" % self.alias
        region_filter = "?region=%s" % self.region_id
        visibility_filter = "?visibility=%s" % self.visibility
        contains_filter = '?contains=%s' \
            % self.flavor_name[str_index1:str_index2]
        startswith_filter = "?starts_with=%s" % self.flavor_name[:str_index2]
        series_filter = "?series=%s" % self.series
        tenant_filter = "?tenant=%s" % self.tenant_id

        for list_filter in [None, region_filter, visibility_filter,
                            alias_filter, contains_filter, startswith_filter,
                            series_filter, tenant_filter]:
            _, body = self.client.list_flavors(list_filter)
            flavor_ids = [flvr["id"] for flvr in body["flavors"]]
            self.assertIn(self.flavor_id, flavor_ids)

    @decorators.idempotent_id('7b9d1f91-a8a4-458d-aaad-a98b5bf033b4')
    def test_create_flavor(self):
        post_body = self._get_flavor_params()
        # call client create_flavor and wait till status equals 'Success'
        _, body = self.client.create_flavor(**post_body)
        flavor = body["flavor"]
        test_flvr_id = flavor['id']
        self._wait_for_flavor_status_on_dcp(flavor["id"], 'Success')

        # do not forget to add this account to addCleanUp
        self.addCleanup(self._del_flv_and_validate_deletion_on_dcp_and_lcp,
                        flavor["id"])

        # verify flavor record created successfully
        flavor = self._get_flavor_details(test_flvr_id)
        self.assertEqual(flavor["visibility"], "private")
        self.assertEqual(flavor["regions"][0]["name"], CONF.identity.region)
        self.assertEqual(flavor["status"], "Success")

    @decorators.idempotent_id('4cad10ce-67d2-4633-b347-2c16783a31b9')
    def test_add_flvr_tags(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # test add_tags command with two sets of key:values
        add_tag_body = {"tags": {"a": "b", "c": "d"}}
        self._exec_tags_function(test_flvr_id, add_tag_body, 'add', None)
        _, tag_body = self.client.get_tags(test_flvr_id)
        self.assertDictEqual(add_tag_body.get("tags"), tag_body.get("tags"))

    @decorators.idempotent_id('db8e5c0f-0041-45d4-9939-e079296123d8')
    def test_replace_flvr_tags(self):
        # setup data for test case and assign two tags
        post_body = self._get_flavor_params()
        tags = {}
        tags["a"] = "b"
        tags["c"] = "d"
        post_body["tag"] = tags
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # test replace_tags command
        replace_tag_body = {"tags": {"e": "f", "g": "h"}}
        self._exec_tags_function(test_flvr_id, replace_tag_body,
                                 'update', None)
        _, tag_body = self.client.get_tags(test_flvr_id)
        self.assertDictEqual(replace_tag_body.get("tags"),
                             tag_body.get("tags"))

    @decorators.idempotent_id('e0a0eca6-e120-45ab-a1a4-f5b95fdf97f1')
    def test_delete_flvr_tag(self):
        # setup data for test case and assign two tags
        post_body = self._get_flavor_params()
        tags = {}
        tags["e"] = "f"
        tags["g"] = "h"
        post_body["tag"] = test_tag_body = tags
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # test delete_tag command - delete the first key in tags body
        delete_tag_key_e = "e"
        self._exec_tags_function(test_flvr_id, None, 'delete',
                                 delete_tag_key_e)
        # do get_tag and confirm that resp body["tag"] now contains only
        # second keypair
        _, tag_body = self.client.get_tags(test_flvr_id)
        test_tag_body.pop(delete_tag_key_e)
        self.assertDictEqual(test_tag_body, tag_body.get("tags"))

    @decorators.idempotent_id('9c511020-53ed-4139-8c53-451cb0ea8c75')
    def test_delete_all_flvr_tags(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        tags = {}
        tags["i"] = "j"
        tags["k"] = "l"
        post_body["tag"] = test_tag_body = tags
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # before execute test, check that "tag" body is populated correctly
        _, tag_body = self.client.get_tags(test_flvr_id)
        self.assertDictEqual(test_tag_body, tag_body.get("tags"))
        # test delete_all_tags command - run get_tag again and confirm
        # that the tag dict is now empty
        self._exec_tags_function(test_flvr_id, None, 'delete', None)
        _, tag_body = self.client.get_tags(test_flvr_id)
        # assert that tag_body contains nothing
        self.assertFalse(tag_body["tags"])

    @decorators.idempotent_id('ec74d68f-b42a-41a8-9685-ff5eca25ea0c')
    def test_add_flvr_region(self):
        # setup data for test case
        post_body = self._get_flavor_params(set_region=False)
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        post_region_body = '{"regions": [{"name": "%s"}]}' % (self.region_id)
        post_region_body = json.loads(post_region_body)
        _, body = self.client.add_flvr_regions(test_flvr_id,
                                               post_region_body)
        self._wait_for_flavor_status_on_dcp(test_flvr_id, 'Success')
        _, body = self.client.get_flavor(test_flvr_id)
        self.assertEqual(body["flavor"]["regions"][0]["name"],
                         post_region_body["regions"][0]["name"])

    @decorators.idempotent_id('5c7e6a94-89d2-4851-bf57-26371da7f47a')
    def test_delete_flvr_region(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # delete the region then check to confirm flavor status
        _, body = self.client.delete_flvr_region(test_flvr_id,
                                                 self.region_id)
        # flavor status must show 'no regions' when it has no region assigned
        self._wait_for_flavor_status_on_dcp(test_flvr_id, 'no regions')
        # flavor region is now empty after the lone region was removed
        _, body = self.client.get_flavor(test_flvr_id)
        self.assertTrue(len(body["flavor"]["regions"]) == 0)

    @decorators.idempotent_id('71404409-5d95-472c-8dac-b49a1c0c4b37')
    def test_add_flvr_extra_specs(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']
        test_dflt_ex_specs = flavor['extra-specs']

        # add a custom extra spec
        add_es_body = {"os_extra_specs": {"a": "apple"}}
        self._exec_ex_spec_function(test_flvr_id, add_es_body, 'add',
                                    None)
        # assert extra specs add results match expected
        test_dflt_ex_specs.update(add_es_body["os_extra_specs"])
        _, flvr_ex_specs = self.client.get_extra_specs(test_flvr_id)
        self.assertDictEqual(test_dflt_ex_specs,
                             flvr_ex_specs.get("os_extra_specs"))

    @decorators.idempotent_id('043948fd-125b-4d96-bf40-42464066a7e1')
    def test_update_flvr_extra_specs(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']
        test_dflt_ex_specs = flavor['extra-specs']

        # run the test
        add_es_body = {"os_extra_specs": {"a": "apple"}}
        replace_es_body = {"os_extra_specs": {"a": "apple", "b": "banana"}}

        # add one custom extra spec , then replace with additional extra spec
        self._exec_ex_spec_function(test_flvr_id, add_es_body, 'add', None)
        # then add another custom extra spec using update_extra_spec
        self._exec_ex_spec_function(test_flvr_id, replace_es_body, 'update',
                                    None)
        # assert extra specs update results match expected
        test_dflt_ex_specs.update(replace_es_body["os_extra_specs"])
        _, flvr_ex_specs = self.client.get_extra_specs(test_flvr_id)
        self.assertDictEqual(test_dflt_ex_specs,
                             flvr_ex_specs.get("os_extra_specs"))

    @decorators.idempotent_id('df83e2cd-d202-4b2f-8459-391a73067ec5')
    def test_delete_flvr_extra_spec(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # run the test
        add_es_body = {"os_extra_specs": {"g": "guava", "h": "honeydew"}}
        delete_es_key_h = "h"
        # add two custom extra specs then do get_extra_specs to save off
        # the extra_spec add results
        self._exec_ex_spec_function(test_flvr_id, add_es_body, 'add', None)
        _, test_ex_specs = self.client.get_extra_specs(test_flvr_id)
        # now delete one of the custom extra specs
        self._exec_ex_spec_function(test_flvr_id, None, 'delete',
                                    delete_es_key_h)
        # assert extra specs update results match expected
        test_ex_specs["os_extra_specs"].pop(delete_es_key_h)
        _, flvr_ex_specs = self.client.get_extra_specs(test_flvr_id)
        self.assertDictEqual(test_ex_specs["os_extra_specs"],
                             flvr_ex_specs.get("os_extra_specs"))

    @decorators.idempotent_id('e3fc7ce3-c8fe-4805-8ad3-7be2c94fe7ad')
    def test_delete_all_flvr_extra_specs(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']
        test_dflt_ex_specs = flavor['extra-specs']

        # run the test
        # add custom extra specs, then validate extra-spec add result
        add_es_body = {"os_extra_specs": {"c": "carrots"}}
        self._exec_ex_spec_function(test_flvr_id, add_es_body, 'add', None)
        _, ex_specs_add_results = self.client.get_extra_specs(test_flvr_id)
        self.assertIn("c", ex_specs_add_results["os_extra_specs"])
        self.assertEqual("carrots",
                         ex_specs_add_results["os_extra_specs"]["c"])
        # run delete ALL extra specs - note that this will only
        # delete custom extra specs, NOT the default extra specs
        self._exec_ex_spec_function(test_flvr_id, None, 'delete', None)
        _, flvr_ex_specs = self.client.get_extra_specs(test_flvr_id)
        # assert that flavor extra specs now contains only
        # the default extra specs
        self.assertDictEqual(test_dflt_ex_specs,
                             flvr_ex_specs.get("os_extra_specs"))

    @decorators.idempotent_id('187195b5-adfb-4c73-a2f5-42117021f5f2')
    def test_add_flvr_tenant(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # check that flavor contains one tenant before testing add_flvr_tenant
        flavor = self._get_flavor_details(test_flvr_id)
        self.assertEqual(len(flavor["tenants"]), 1)

        # test add_flvr_tenant by adding one more tenant
        post_tenant_body = '{"tenants": ["%s"]}' % (self.alt_tenant_id)
        post_tenant_body = json.loads(post_tenant_body)
        _, body = self.client.add_flvr_tenants(test_flvr_id, post_tenant_body)
        self._wait_for_flavor_status_on_dcp(test_flvr_id, 'Success')

        # get flavor on same flavor id and confirm we have two tenants now
        flavor = self._get_flavor_details(test_flvr_id)
        self.assertEqual(len(flavor["tenants"]), 2)

    @decorators.idempotent_id('a7c976cd-6064-4279-ab64-2575d091cdae')
    def test_delete_flvr_tenant(self):
        # setup data for test case and assign two tags
        post_body = self._get_flavor_params(single_tenant=False)
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']

        # checking that flavor created contains two tenants
        flavor = self._get_flavor_details(test_flvr_id)
        self.assertEqual(len(flavor["tenants"]), 2)

        # delete one tenant, then wait until status = 'Success'
        _, body = self.client.delete_flvr_tenant(test_flvr_id,
                                                 self.alt_tenant_id)
        self._wait_for_flavor_status_on_dcp(test_flvr_id, 'Success')
        # get flavor to confirm flavor["tenants"] now shows one tenant only
        flavor = self._get_flavor_details(test_flvr_id)
        self.assertEqual(len(flavor["tenants"]), 1)

    @decorators.idempotent_id('36958bba-673e-4397-85a9-fddb01e9ca0d')
    def test_delete_flavor(self):
        # setup data for test case
        post_body = self._get_flavor_params()
        flavor = self._create_flv_and_validate_creation_on_dcp_and_lcp(
            **post_body)
        test_flvr_id = flavor['id']

        # delete the data and do get_flavor to ensure 404-NotFound response
        self._del_flv_and_validate_deletion_on_dcp_and_lcp(test_flvr_id)
        self.assertRaises(exceptions.NotFound, self.client.get_flavor,
                          test_flvr_id)

    @decorators.idempotent_id('2a1240d8-ae30-4c37-b99f-af961a5e16cb')
    def test_create_flavor_with_swap_and_ephemeral(self):
        post_body = self._get_flavor_params()

        # set swap and ephemeral size
        swap = ephemeral = 1024
        # update swap and ephemeral
        post_body['ephemeral'] = swap
        post_body['swap'] = ephemeral
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']
        # verify flavor record created successfully
        flavor_details = self._get_flavor_details(test_flvr_id)
        self.assertEqual(flavor_details["status"], "Success")
        self.assertEqual(flavor_details["swap"], swap)
        self.assertEqual(flavor_details["ephemeral"], ephemeral)

    @decorators.idempotent_id('53275983-6999-42f2-8ce5-6a83ade3980f')
    def test_create_flavor_with_disk(self):
        post_body = self._get_flavor_params()

        # set disk size
        disk = 100
        # update disk
        post_body['disk'] = disk
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']
        # verify flavor record created successfully
        flavor_details = self._get_flavor_details(test_flvr_id)
        self.assertEqual(flavor_details["status"], "Success")
        self.assertEqual(flavor_details["disk"], disk)

    @decorators.idempotent_id('2178be75-c36b-4cfe-9df7-8a4bff6e7f83')
    def test_list_flavor_with_additional_field(self):
        _, body = self.client.list_flavors()

        fields = [
            'id',
            'description',
            'series',
            'ram',
            'vcpus',
            'disk',
            'swap',
            'ephemeral',
            'extra-specs',
            'options',
            'tag',
            'regions',
            'visibility',
            'tenants',
        ]

        # check if it has minimum one value
        if body["flavors"]:
            flavor = body["flavors"][0]
            # check fields is present in response dict as keys
            self.assertTrue(set(fields).issubset(set(flavor.keys())))

    @decorators.idempotent_id('997ca03c-4176-4632-a0c9-7e943b03306c')
    def test_create_flavor_with_region_group(self):
        post_body = self._get_flavor_params()

        # region group
        region_group = {'name':'NCLargetest', 'type': 'group'}
        # update region_group to regions
        post_body['regions'].append(region_group)
        flavor = self._data_setup(post_body)
        test_flvr_id = flavor['id']
        # verify flavor record created successfully
        flavor_details = self._get_flavor_details(test_flvr_id)
        self.assertEqual(flavor_details["status"], "Success")
        self.assertDictEqual(flavor["regions"][1], region_group)

    @decorators.idempotent_id('997ca03c-4176-4632-a0c9-7e943b03306d')
    def test_create_flavor_with_uuid(self):
        post_body = self._get_flavor_params()
        # update uuid
        str_uuid = uuid.uuid4().hex
        post_body['id'] = str_uuid
        flavor = self._data_setup(post_body)
        # verify flavor record created successfully
        flavor_details = self._get_flavor_details(str_uuid)
        self.assertEqual(flavor_details["status"], "Success")
        self.assertDictEqual(flavor["id"][1], str_uuid)