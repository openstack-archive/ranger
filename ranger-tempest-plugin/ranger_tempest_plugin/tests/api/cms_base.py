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

import random
import time
import uuid

from oslo_log import log as logging

from ranger_tempest_plugin.tests.api import base

from tempest import config

from tempest.common.utils import data_utils
from tempest.lib import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class CmsBaseOrmTest(base.BaseOrmTest):
    credentials = ['admin', 'primary', 'alt']

    @classmethod
    def setup_clients(cls):
        super(CmsBaseOrmTest, cls).setup_clients()
        cls.client = cls.os_primary.cms_client

    @classmethod
    def _get_quota(cls):
        compute, storage, network, quota = {}, {}, {}, {}
        compute["instances"] = "10"
        compute["injected-files"] = "10"
        compute["key-pairs"] = "10"
        compute["ram"] = "10"
        compute["vcpus"] = "51"
        compute["metadata-items"] = "34"
        compute["injected-file-content-bytes"] = "25"

        storage["gigabytes"] = "10"
        storage["snapshots"] = "10"
        storage["volumes"] = "10"

        network["floating-ips"] = "10"
        network["networks"] = "10"
        network["ports"] = "10"
        network["routers"] = "10"
        network["subnets"] = "10"
        network["security-group-rules"] = "51"
        network["security-groups"] = "50"

        quota['compute'] = [compute]
        quota['storage'] = [storage]
        quota['network'] = [network]
        return quota

    @classmethod
    def _get_additional_quota_for_cust(cls):
        quota = cls._get_quota()
        quota["compute"][0]["floating-ips"] = "10"
        quota["compute"][0]["fixed-ips"] = "10"
        quota["compute"][0]["injected-file-path-bytes"] = "34"
        quota["compute"][0]["server-groups"] = "10"
        quota["compute"][0]["server-group-members"] = "34"
        quota["network"][0]["health-monitor"] = "10"
        quota["network"][0]["member"] = "10"
        quota["network"][0]["nat-instance"] = "10"
        quota["network"][0]["pool"] = "10"
        quota["network"][0]["route-table"] = "10"
        quota["network"][0]["vip"] = "10"
        return quota

    @classmethod
    def _get_customer_quota(cls, name):
        payload = {}
        payload['name'] = name
        payload['type'] = 'single'
        payload['quotas'] = [cls._get_quota()]
        return payload

    @classmethod
    def _get_customer_params(cls, quota=None, enabled=True,
                             region_users=True, default_users=True,
                             region_type='single', add_uuid=False):
        region, user, tags, payload = {}, {}, {}, {}
        cust_name = data_utils.rand_name('ormTempestCms')
        if not quota:
            quota = cls._get_quota()
        region['name'] = CONF.identity.region
        region['type'] = region_type
        region['quotas'] = [quota]
        user['id'] = cls.os_primary.credentials.username
        user['role'] = ["admin"]
        region["users"] = [user] if region_users else []
        regions = [region]
        tags['my_server_name'] = cust_name
        tags['ocx_cust'] = random.randint(0, 999999999)
        payload["description"] = cust_name
        payload["enabled"] = True if enabled else False
        payload["name"] = cust_name
        payload['tags'] = tags
        payload["regions"] = regions
        payload["defaultQuotas"] = [quota]
        payload['users'] = [user] if default_users else []

        if add_uuid:
            payload['uuid'] = uuid.uuid4()

        return payload

    @classmethod
    def _get_customer_params_diff_region_user(cls):
        payload = cls._get_customer_params(default_users=True)
        payload['regions'] = [{
            'users': [{
                'id': cls.os_alt.credentials.username,
                'role': ["admin"]
            }],
        }]
        return payload

    @classmethod
    def _get_customer_additional_quota(cls):
        payload = cls._get_customer_params(region_users=True)
        payload['regions'][0]['quotas'] = cls._get_additional_quota_for_cust()
        return payload

    @classmethod
    def _get_bare_customer_params(cls):
        customer = {}
        customer['description'] = ''
        customer['enabled'] = True
        customer['name'] = data_utils.rand_name('ormTempestCms')
        customer['regions'] = []
        customer['defaultQuotas'] = []
        customer['users'] = []
        return customer

    @classmethod
    def _get_user_params(cls, alt=False):
        users = []
        if not alt:
            users.append({'id': cls.os_primary.credentials.username,
                          'role': ['admin']})
        else:
            users.append({'id': cls.os_alt.credentials.username,
                          'role': ['admin_viewer', 'admin_support']})
        return users

    @classmethod
    def _get_region_params(cls):
        quota = cls._get_quota()
        region = {}
        region['name'] = CONF.identity.region
        region['type'] = 'single'
        region['quotas'] = [quota]
        return [region]

    @classmethod
    def _create_cust_validate_creation_on_dcp_and_lcp(self, **kwargs):
        """Creates a customer record:  kwargs contains field data needed for

        customer POST body:
        - name
        - description
        - enabled
        - tags
        - regions
        - defaultQuotas
        - ephemeral
        - regions
        - visibility
        - tenants
        """
        _, body = self.client.create_customer(**kwargs)
        customer_id = body["customer"]["id"]
        _, customer = self.client.get_customer(customer_id)
        if customer["name"] == kwargs["name"]:
            if customer["regions"] == []:
                customer_status = "no regions"
            else:
                customer_status = "Success"

            self._wait_for_status(customer_id, customer_status)
            return customer_id
        else:
            message = "customer %s not created successfully" % kwargs["name"]
            exceptions.TempestException(message)

    @classmethod
    def _wait_for_status(cls, customer_id, status):
        customer_status = cls.client.get_customer(customer_id)[1]["status"]
        start = int(time.time())
        while customer_status != status:
            time.sleep(cls.build_interval)
            customer_status = cls.client.get_customer(customer_id)[1]["status"]
            if customer_status == 'Error':
                message = ('customer %s failed to reach %s status'
                           ' and is in ERROR status on orm' %
                           (customer_id, status))
                raise exceptions.TempestException(message)
            if int(time.time()) - start >= cls.build_timeout:
                message = ('customer %s failed to reach %s'
                           'status within the required time (%s s)'
                           'on orm and is in %s status.'
                           % (customer_id, status,
                              cls.build_timeout,
                              customer_status))
                raise exceptions.TimeoutException(message)

    @classmethod
    def _validate_cust_quota_on_lcp(cls, quota, cust_id):
        expected_quota_count = len(quota["compute"][0]) +\
            len(quota["storage"][0]) +\
            len(quota["network"][0])
        actual_quota_count = 0
        body = cls.nova_quotas_client.show_quota_set(cust_id)
        for param in quota["compute"][0]:
            if param in body["quota_set"]:
                if (quota["compute"][0][param] ==
                        str(body["quota_set"][param])):
                    actual_quota_count += 1
        body = cls.volume_quotas_client.show_quota_set(cust_id)
        for param in quota["storage"][0]:
            if param in body["quota_set"]:
                if str(body["quota_set"][param]) == quota["compute"][0][param]:
                    actual_quota_count += 1
        body = cls.networks_quotas_client.show_quotas(cust_id)
        for param in quota["network"][0]:
            if param in body["quota_set"]:
                if (quota["compute"][0][param] ==
                        str(body["quota_set"][param])):
                    actual_quota_count += 1
        if expected_quota_count == actual_quota_count:
            return True
        else:
            return False

    @classmethod
    def _validate_users_on_cust_on_dcp_and_lcp(cls, post_body, cust_id):
        default_users_req, region_users_req, \
            default_users_dcp, region_users_dcp, \
            users_lcp = [], [], [], [], []
        for user in post_body["regions"][0]["users"]:
            region_users_req.append(user["id"])
        for user in post_body["users"]:
            default_users_req.append(user["id"])
        expected_users_count = len(region_users_req) + len(default_users_req)
        actual_users_count = 0
        lcp_body = cls.identity_client.list_tenant_users(cust_id)
        for user in lcp_body["users"]:
            users_lcp.append(user["id"])
        dcp_body = cls.client.get_customer(cust_id)
        for user in dcp_body["regions"][0]["users"]:
            region_users_dcp.append(user["id"])
        for user in dcp_body["users"]:
            default_users_dcp.append(user["id"])
        for user in default_users_req:
            if (user in users_lcp) and (user in default_users_dcp):
                actual_users_count += 1
        for user in region_users_req:
            if (user in users_lcp) and (user in region_users_dcp):
                actual_users_count += 1
        if expected_users_count == actual_users_count:
            return True
        else:
            return False

    @classmethod
    def _del_cust_validate_deletion_on_dcp_and_lcp(cls, customer_id):
        _, customer = cls.client.get_customer(customer_id)
        regions_on_customer = [region for region in customer["regions"]]
        if regions_on_customer:
            region_name_on_customer = regions_on_customer[0]["name"]
            cls._delete_region_from_customer_and_validate_deletion(
                customer_id, region_name_on_customer)
        cls.client.delete_customer(customer_id)
        cls._wait_for_customer_deletion_on_dcp(customer_id)
        cls._validate_customer_deletion_on_lcp(customer_id)

    @classmethod
    def _delete_region_from_customer_and_validate_deletion(
            cls, customer_id, rname):
        _, region = cls.os_admin.rms_client.get_region(rname)
        region_id = region["id"]
        cls.client.delete_region_from_customer(customer_id, region_id)
        # cls._wait_for_cust_status_on_dcp(customer_id, "no regions")
        cls._wait_for_status(customer_id, "no regions")
        _, body = cls.client.get_customer(customer_id)
        regions_on_customer = [rgn for rgn in body["regions"]]
        if regions_on_customer:
            message = "Region %s failed to get deleted from customer %s " % (
                rname, customer_id)
            raise exceptions.TempestException(message)
        cls._validate_customer_deletion_on_lcp(customer_id)

    @classmethod
    def _wait_for_customer_deletion_on_dcp(cls, customer_id):
        _, body = cls.client.list_customers()
        customer_list = body["customers"]
        customer_ids = [customer["id"]
                        for customer in customer_list
                        if customer["id"] == customer_id]
        start = int(time.time())
        while customer_ids:
            time.sleep(cls.build_interval)
            _, body = cls.client.list_customers()["customers"]
            customer_list = body["customers"]
            customer_ids = [customer["id"]
                            for customer in customer_list
                            if customer["id"] == customer_id]
            if customer_ids:
                customer_status = customer_ids[0]["status"]
                if customer_status == 'Error':
                    message = "customer %s failed to get deleted and is in\
                        error status" % customer_id
                    raise exceptions.TempestException(message)
            if int(time.time()) - start >= cls.build_timeout:
                message = (
                    'customer %s failed to get deleted within '
                    'the required time (%s s) and is in %s status.'
                    % (customer_id, cls.build_timeout,
                        customer_status))
                raise exceptions.TimeoutException(message)

    @classmethod
    def _validate_customer_deletion_on_lcp(cls, customer_id):
        body = cls.identity_client.list_projects()["projects"]
        customer_ids = [customer["id"]
                        for customer in body
                        if customer["id"] == customer_id]
        if customer_ids:
            message = "customer %s failed to get deleted on lcp" \
                      % customer_id
            raise exceptions.TempestException(message)

    @classmethod
    def _update_cust_and_validate_status_on_dcp_and_lcp(
            cls, customer_id, para, **kwargs):
        body = cls.client.update_customer(customer_id, para, **kwargs)
        if body["id"] == customer_id:
            cls._wait_for_cust_status_on_dcp(customer_id, "Success")
            cls._validate_cust_creation_on_lcp(customer_id)
        else:
            message = "customer %s not updated successfully" % customer_id
            raise exceptions.TempestException(message)
        return body
