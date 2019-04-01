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

import time

from oslo_log import log as logging
from ranger_tempest_plugin.tests.api import base
from tempest.common.utils import data_utils
from tempest import config
from tempest.lib import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class GrpBaseOrmTest(base.BaseOrmTest):
    credentials = ['admin', 'primary', 'alt']

    @classmethod
    def setup_clients(cls):
        super(GrpBaseOrmTest, cls).setup_clients()
        cls.client = cls.os_primary.grp_client

    @classmethod
    def _get_group_params(cls, enabled=True):
        region, payload = {}, {}
        grp_name = data_utils.rand_name('ormTempestGrp')
        domain_name = CONF.auth.admin_domain_name
        region['name'] = CONF.identity.region
        region['type'] = 'single'
        regions = [region]
        payload["description"] = grp_name
        payload["domain_name"] = domain_name
        payload["enabled"] = True if enabled else False
        payload["name"] = grp_name
        payload["regions"] = regions
        return payload

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
        region = {}
        region['name'] = CONF.identity.region
        region['type'] = 'single'
        return [region]

    @classmethod
    def _create_grp_validate_creation_on_dcp_and_lcp(self, **kwargs):
        """ Creates a keystone group record:  kwargs contains field data
        needed for group customer POST body:
        - name
        - description
        - enabled
        - domain_name
        - regions
        """
        _, body = self.client.create_group(**kwargs)
        group_id = body["group"]["id"]
        _, group = self.client.get_group(group_id)
        if group["name"] == kwargs["name"]:
            if group["regions"] == []:
                group_status = "no regions"
            else:
                group_status = "Success"

            self._wait_for_group_status(group_id, group_status)
            return group_id
        else:
            message = "group  %s not created successfully" % kwargs["name"]
            exceptions.TempestException(message)

    @classmethod
    def _wait_for_group_status(cls, group_id, status):
        group_status = cls.client.get_group(group_id)[1]["status"]
        start = int(time.time())
        while group_status != status:
            time.sleep(cls.build_interval)
            group_status = cls.client.get_group(group_id)[1]["status"]
            if group_status == 'Error':
                message = ('group %s failed to reach %s status'
                           ' and is in ERROR status on orm' %
                           (group_id, status))
                raise exceptions.TempestException(message)
            if int(time.time()) - start >= cls.build_timeout:
                message = ('group %s failed to reach %s'
                           'status within the required time (%s s)'
                           'on orm and is in %s status.'
                           % (group_id, status,
                              cls.build_timeout,
                              group_status))
                raise exceptions.TimeoutException(message)

    @classmethod
    def _del_group_validate_deletion_on_dcp_and_lcp(cls, group_id):
        _, group = cls.client.get_group(group_id)
        regions_on_group = [region for region in group["regions"]]
        if regions_on_group:
            region_name_on_group = regions_on_group[0]["name"]
            cls._delete_region_from_group_and_validate_deletion(
                group_id, region_name_on_group)
        cls.client.delete_group(group_id)
        cls._wait_for_group_deletion_on_dcp(group_id)
        cls._validate_group_deletion_on_lcp(group_id)

    @classmethod
    def _delete_region_from_group_and_validate_deletion(
            cls, group_id, rname):
        _, region = cls.os_admin.rms_client.get_region(rname)
        region_id = region["id"]
        cls.client.delete_region_from_group(group_id, region_id)
        cls._wait_for_group_status(group_id, "no regions")
        _, body = cls.client.get_group(group_id)
        regions_on_group = [rgn for rgn in body["regions"]]
        if regions_on_group:
            message = "Region %s failed to get deleted from group %s " % (
                rname, group_id)
            raise exceptions.TempestException(message)

    @classmethod
    def _wait_for_group_deletion_on_dcp(cls, group_id):
        _, body = cls.client.list_groups()
        group_list = body["groups"]
        group_ids = [group["id"] for group in group_list
                     if group["id"] == group_id]
        start = int(time.time())
        while group_ids:
            time.sleep(cls.build_interval)
            _, body = cls.client.list_groups()["groups"]
            group_list = body["groups"]
            group_ids = [group["id"] for group in group_list
                         if group["id"] == group_id]
            if group_ids:
                group_status = group_ids[0]["status"]
                if group_status == 'Error':
                    message = "group %s failed to get deleted and is in\
                        error status" % group_id
                    raise exceptions.TempestException(message)
            if int(time.time()) - start >= cls.build_timeout:
                message = (
                    'group %s failed to get deleted within '
                    'the required time (%s s) and is in %s status.'
                    % (group_id, cls.build_timeout,
                        group_status))
                raise exceptions.TimeoutException(message)

    @classmethod
    def _validate_group_deletion_on_lcp(cls, group_id):
        _, body = cls.client.list_groups()
        group_ids = [group["id"] for group in body["groups"]
                     if group["id"] == group_id]
        if group_ids:
            message = "group %s failed to get deleted on lcp" \
                      % group_id
            raise exceptions.TempestException(message)
