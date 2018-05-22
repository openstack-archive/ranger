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

from aic_orm_tempest_plugin.tests.api import base

from oslo_log import log as logging

from tempest import config

from tempest.lib import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class FmsBaseOrmTest(base.BaseOrmTest):
    credentials = ['admin', 'primary', 'alt']

    # added setup_clients function by stew
    @classmethod
    def setup_clients(cls):
        super(FmsBaseOrmTest, cls).setup_clients()
        cls.client = cls.os_primary.fms_client
        cls.flavors_client = cls.os_admin.flavors_client
        cls.tenant_id = cls._get_tenant_id(
            cls.os_primary.credentials.tenant_name)
        cls.alt_tenant_id = cls._get_tenant_id(
            cls.os_alt.credentials.tenant_name)

    @classmethod
    def _get_flavor_params(cls, set_region=True, single_tenant=True):
        post_body, region = {}, {}
        region["name"] = CONF.identity.region
        ram = random.randint(1, 4) * 1024
        swap = random.randint(1, 40) * 1024
        vcpus = random.randint(2, 46)
        disk = random.randint(2, 102)
        post_body["description"] = \
            "orm-plugin-BaseORMTest-flavor"
        post_body["series"] = random.choice(["ns", "nd", "gv", "nv"])
        post_body["alias"] = "flavor_alias"
        post_body["ram"] = str(ram)
        post_body["vcpus"] = str(vcpus)
        post_body["disk"] = str(disk)
        post_body["swap"] = str(swap)
        post_body["ephemeral"] = "1024"
        post_body["regions"] = [region] if set_region else []
        post_body["visibility"] = "private"

        if single_tenant:
            post_body["tenants"] = [cls.tenant_id]
        else:
            post_body["tenants"] = [cls.tenant_id, cls.alt_tenant_id]
        return post_body

    @classmethod
    def _create_flv_and_validate_creation_on_dcp_and_lcp(cls, **kwargs):
        """ kwargs contain all field data needed in a flavor POST body:
           - name
           - description
           - alias
           - ram
           - vcpus
           - disk
           - swap
           - ephemeral
           - regions
           - visibility
           - tenants
        """
        _, body = cls.client.create_flavor(**kwargs)
        flavor = body["flavor"]
        flavor_id = flavor["id"]
        _, body = cls.client.get_flavor(flavor_id)
        flavor_detail = body["flavor"]
        if flavor_detail["vcpus"] == kwargs["vcpus"]:
            if flavor_detail["regions"] == []:
                flavor_status = "no regions"
            else:
                flavor_status = "Success"
            flavor_id = flavor_detail["id"]
            cls._wait_for_flavor_status_on_dcp(flavor_id, flavor_status)
            cls._validate_flavor_creation_on_lcp(flavor_id)
            return flavor
        else:
            message = "flavor %s not created successfully" % flavor_id
            raise exceptions.TempestException(message)

    @classmethod
    def _wait_for_flavor_status_on_dcp(cls, flavor_id, status):
        _, body = cls.client.get_flavor(flavor_id)
        flavor = body["flavor"]
        flavor_status = flavor["status"]
        start = int(time.time())
        while flavor_status != status:
            time.sleep(cls.build_interval)
            _, body = cls.client.get_flavor(flavor_id)
            flavor = body["flavor"]
            flavor_status = flavor["status"]
            if flavor_status == 'Error':
                message = ('flavor %s failed to reach %s status'
                           ' and is in ERROR status on orm' %
                           (flavor_id, status))
                raise exceptions.TempestException(message)
            if int(time.time()) - start >= cls.build_timeout:
                message =\
                    'flavor %s failed to reach %s status within'
                ' the required time (%s s) on orm and is in'
                '%s status.' % (flavor_id, status,
                                cls.build_timeout, flavor_status)
                raise exceptions.TimeoutException(message)

    @classmethod
    def _validate_flavor_creation_on_lcp(cls, flavor_id):
        _, body = cls.client.list_flavors()
        flavor = [flavor["id"] for flavor in body["flavors"]
                  if flavor["id"] == flavor_id]
        if not flavor:
            message = "flavor %s not in nova flavor list" % flavor_id
            raise exceptions.TempestException(message)

    @classmethod
    def _validate_flv_extraspecs_on_dcp_and_lcp(cls, flavor_id,
                                                expected_specs):
        expected_specs_count = len(expected_specs)
        _, body = cls.client.get_flavor(flavor_id)
        flavor_orm = body["flavor"]
        flavor_lcp = cls.flavors_client.show_flavor(flavor_id)["flavor"]

        def _validate_extra_specs(flv):
            actual_specs_count = 0
            actual_specs = {}
            for spec in flv["extra-specs"]:
                actual_specs[spec] = flv["extra-specs"][spec]
            for spec in expected_specs:
                if spec in actual_specs:
                    if expected_specs[spec] == actual_specs[spec]:
                        actual_specs_count += 1
            if expected_specs_count == actual_specs_count:
                return True
            else:
                return False
        if _validate_extra_specs(flavor_orm) and\
                _validate_extra_specs(flavor_lcp):
            return True
        else:
            return False

    @classmethod
    def _del_flv_and_validate_deletion_on_dcp_and_lcp(cls, flavor_id):
        _, body = cls.client.get_flavor(flavor_id)
        regions_on_flavor = [region for region in body["flavor"]["regions"]]
        if regions_on_flavor:
            region_name_on_flavor = regions_on_flavor[0]["name"]
            cls._delete_region_from_flavor_and_validate_deletion(
                flavor_id, region_name_on_flavor)
        cls.client.delete_flavor(flavor_id)
        cls._wait_for_flavor_deletion_on_dcp(flavor_id)
        cls._validate_flavor_deletion_on_lcp(flavor_id)

    @classmethod
    def _delete_region_from_flavor_and_validate_deletion(
            cls, flavor_id, rname):
        _, body = cls.rms_client.get_region(rname)
        region_id = body["id"]
        cls.client.delete_region_from_flavor(flavor_id, region_id)
        cls._wait_for_flavor_status_on_dcp(flavor_id, "no regions")
        _, body = cls.client.get_flavor(flavor_id)
        regions_on_flavor = body["flavor"]["regions"]

        if regions_on_flavor:
            message = \
                "Region %s failed to get deleted from flavor %s " % (
                    rname, flavor_id)
            raise exceptions.TempestException(message)
        cls._validate_flavor_deletion_on_lcp(flavor_id)

    @classmethod
    def _wait_for_flavor_deletion_on_dcp(cls, flavor_id):
        _, body = cls.client.list_flavors()
        flavor_ids = [flavor["id"] for flavor in body["flavors"]
                      if flavor["id"] == flavor_id]
        start = int(time.time())
        while flavor_ids:
            time.sleep(cls.build_interval)
            _, body = cls.client.list_flavors()
            flavor_ids = [flavor["id"] for flavor in body["flavors"]
                          if flavor["id"] == flavor_id]
            if flavor_ids:
                flavor_status = flavor_ids[0]["status"]
                if flavor_status == 'Error':
                    message = \
                        'Flavor %s failed to get deleted'
                    'and is in error status' % \
                        flavor_id
                    raise exceptions.TempestException(message)
            if int(time.time()) - start >= cls.build_timeout:
                message = (
                    'flavor %s failed to get deleted within '
                    'the required time (%s s) and is in %s status.'
                    % (flavor_id, cls.build_timeout, flavor_status))
                raise exceptions.TimeoutException(message)

    @classmethod
    def _validate_flavor_deletion_on_lcp(cls, flavor_id):
        body = cls.flavors_client.list_flavors()["flavors"]
        flavor_ids = [flavor["id"] for flavor in body
                      if flavor["id"] == flavor_id]
        if flavor_ids:
            flavor_status = cls.flavors_client.show_flavor(
                flavor_id)["flavor"]["status"]
            message = "flavor %s failed to get deleted and is in %s status" \
                      % (flavor_id, flavor_status)
            raise exceptions.TempestException(message)

    @classmethod
    def _get_tenant_id(cls, tenant_name):
        body = cls.identity_client.list_tenants()
        for tenant in body["tenants"]:
            if(tenant["name"] == tenant_name):
                return tenant["id"]
        message = ('tenant %s not found on tenant list' % cls.tenant_name)
        raise exceptions.TempestException(message)

    @classmethod
    def _get_expected_flavor_name(cls, post_body):
        name = post_body["series"] + "." + "c" + \
            post_body["vcpus"] + "r" + \
            str(int(post_body["ram"]) / 1024) \
            + "d" + post_body["disk"] + "s" + \
            str(int(post_body["swap"]) / 1024) \
            + "e" + str(int(post_body["ephemeral"]) / 1024)
        return name

    @classmethod
    def _validate_flv_geometry_on_lcp(cls, flavor_id, post_body):
        flv = cls.flavors_client.show_flavor(flavor_id)["flavor"]
        if flv["vcpus"] == int(post_body["vcpus"]) and \
                flv["ram"] == post_body["ram"] and \
                flv["swap"] == int(post_body["swap"]) and \
                flv["disk"] == int(post_body["disk"]) and \
                flv["ephemeral"] == post_body["ephemeral"]:
            return True
        else:
            return False
