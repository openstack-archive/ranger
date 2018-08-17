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

from ranger_tempest_plugin.tests.api import base

from oslo_log import log as logging

from tempest import config

from tempest.common.utils import data_utils

from tempest.lib import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class ImsBaseOrmTest(base.BaseOrmTest):
    credentials = ['admin', 'primary', 'alt']

    @classmethod
    def setup_clients(cls):
        super(ImsBaseOrmTest, cls).setup_clients()
        # service clients
        cls.client = cls.os_primary.ims_client
        cls.rms_client = cls.os_primary.rms_client
        cls.cms_client = cls.os_primary.cms_client

        # setup variables
        cls.region_id = CONF.identity.region
        cls.tenant_id = cls._get_tenant_id(
            cls.os_primary.credentials.tenant_name)
        cls.alt_tenant_id = cls._get_tenant_id(
            cls.os_alt.credentials.tenant_name)

    @classmethod
    def _get_image_params(cls, set_region=True, single_tenant=True,
                          set_private=True, set_enabled=True):
        region, post_body = {}, {}
        post_body["name"] = data_utils.rand_name(
            "orm-plugin-TestTempestIms-image")

        # use ubuntu website for the image location URL
        ubuntu_url = "http://archive.ubuntu.com/"
        ubuntu_dir = "ubuntu/dists/xenial/main/installer-i386/current/images/"
        ubuntu_iso = "netboot/mini.iso"
        post_body["url"] = ubuntu_url + ubuntu_dir + ubuntu_iso

        post_body["disk-format"] = "qcow2"
        post_body["container-format"] = "bare"

        region["name"] = cls.region_id
        region["type"] = "single"
        region["checksum"] = "7297321c2fa6424417a548c85edd6e98"
        region["virtual_size"] = "None"
        region["size"] = "38797312"

        # set enabled status to True or False based on set_enabled value
        post_body["enabled"] = True if set_enabled else False
        # add region for the image as needed
        post_body["regions"] = [region] if set_region else []
        # create image with visibililty = "public" or "private"
        post_body["visibility"] = "private" if set_private else "public"
        # add tenant for the image only if set_private
        if set_private:
            if single_tenant:
                post_body["customers"] = [cls.tenant_id]
            else:
                post_body["customers"] = [cls.tenant_id, cls.alt_tenant_id]
        else:
            post_body["customers"] = []

        return post_body

    @classmethod
    def _get_tenant_id(cls, tenant_name):
        body = cls.identity_client.list_tenants()
        for tenant in body["tenants"]:
            if(tenant["name"] == tenant_name):
                return tenant["id"]
        message = ('tenant %s not found on tenant list' % cls.tenant_name)
        raise exceptions.TempestException(message)

    @classmethod
    def _create_img_and_validate_creation_on_dcp_and_lcp(cls, **kwargs):
        _, body = cls.client.create_image(**kwargs)
        image = body["image"]
        image_id = image["id"]

        _, body = cls.client.get_image(image_id)
        image_detail = body["image"]
        if image_detail["name"] == kwargs["name"]:
            if image_detail["regions"] == []:
                image_status = "no regions"
            else:
                image_status = "Success"

            cls._wait_for_image_status_on_dcp(image_id, image_status)
            return image
        else:
            message = ('image %s not created successfully' % kwargs["name"])
            raise exceptions.TempestException(message)

    @classmethod
    def _wait_for_image_status_on_dcp(cls, image_id, status):
        _, body = cls.client.get_image(image_id)
        image_status = body["image"]["status"]
        start = int(time.time())
        while image_status != status:
            time.sleep(cls.build_interval)
            _, body = cls.client.get_image(image_id)
            image_status = body["image"]["status"]
            if image_status == 'Error':
                message = ('Image %s failed to reach %s status'
                           ' and is in ERROR status on orm' %
                           (image_id, status))
                raise exceptions.TempestException(message)
            if int(time.time()) - start >= cls.build_timeout:
                message = ('Image %s failed to reach %s'
                           ' status within ''the required time (%s s)'
                           ' on orm and is in %s status.'
                           % (image_id, status,
                              cls.build_timeout,
                              image_status))
                raise exceptions.TimeoutException(message)

    @classmethod
    def _validate_image_status_on_lcp(cls, image_id, status):
        _, body = cls.client.list_images()["images"]
        image_ids = [image["id"] for image in body]
        if image_id not in image_ids:
            message = ('Image %s not in image list on LCP' % image_id)
            raise exceptions.TempestException(message)
        else:
            image_status = cls.client.show_image()["image"]["status"]
            if image_status != status:
                message = ('Image %s is in %s status instead of %s on LCP.'
                           % (image_id, image_status, status))
                raise exceptions.TempestException(message)

    @classmethod
    def _update_img_validate_status_on_dcp_and_lcp(cls, image_id, para=None,
                                                   **kwargs):
        if para:
            cls.client.update_image(image_id, para, **kwargs)
        else:
            cls.client.update_image(image_id, **kwargs)
        cls._wait_for_image_status_on_dcp(image_id, "Success")
        cls._validate_image_status_on_lcp(image_id, "active")

    @classmethod
    def _del_img_validate_deletion_on_dcp_and_lcp(cls, image_id):
        _, body = cls.client.get_image(image_id)
        image = body["image"]

        regions_on_image = [region for region in image["regions"]]
        if regions_on_image:
            region_id = regions_on_image[0]["name"]
            cls._delete_region_from_image_and_validate_deletion(
                image_id, region_id)

        cls.client.delete_image(image_id)
        cls._validate_image_deletion_on_lcp(image_id)

    @classmethod
    def _delete_region_from_image_and_validate_deletion(cls, image_id,
                                                        region_id):
        cls.client.delete_region_from_image(image_id, region_id)
        cls._wait_for_image_status_on_dcp(image_id, "no regions")

    @classmethod
    def _wait_for_image_deletion_on_dcp(cls, image_id):
        _, body = cls.client.list_images()
        image_ids = [image["id"] for image in body["images"]]
        if image_id in image_ids:
            start = int(time.time())
            while image_id in image_ids:
                time.sleep(cls.build_interval)
                _, image_list = cls.client.list_images()["images"]
                image_ids = [image["id"]
                             for image in image_list if image["id"] ==
                             image_id]
                if image_ids:
                    image_status = image_list[0]["status"]
                    _, body = cls.client.list_images()["images"]
                    image_ids = [image["id"] for image in body]
                    if image_id in image_ids:
                        image_status = image_ids[0]["status"]
                        if image_status == 'Error':
                            message = \
                                'Image %s failed to get deleted '
                            'and is in error status' % \
                                image_id
                            raise exceptions.TempestException(message)
                if int(time.time()) - start >= cls.build_timeout:
                    message = ('Image %s failed to get deleted within '
                               'the required time (%s s) on orm '
                               'and is in %s status.'
                               % (image_id, cls.build_timeout, image_status))
                    raise exceptions.TimeoutException(message)

    @classmethod
    def _validate_image_deletion_on_lcp(cls, image_id):
        _, body = cls.client.list_images()
        image_ids = [image["id"] for image in body["images"]
                     if image["id"] == image_id]
        if image_id in image_ids:
            image_status = body["status"]
            message = "image %s failed to get deleted and is in %s status" \
                % (image_id, image_status)
            raise exceptions.TempestException(message)

    @classmethod
    def _validate_custs_on_img_on_dcp_and_lcp(cls, image_id,
                                              expected_customers):
        expected_customers = sorted(expected_customers)

        _, actual_customers_orm = sorted(
            cls.client.get_image(image_id)["customers"])
        members = cls.client.member_list(image_id)["members"]
        actual_customers_lcp =\
            sorted([member["member_id"] for member in members])
        if actual_customers_orm != expected_customers:
            message = (
                'Incorrect customers on image on orm.'
                'expected customers = %s, actual customers = %s'
                % (expected_customers, actual_customers_orm))
            raise exceptions.TempestException(message)
        if actual_customers_lcp != expected_customers:
            message = (
                'Incorrect customers on image on orm.'
                'expected customers = %s, actual customers = %s'
                % (expected_customers, actual_customers_lcp))
            raise exceptions.TempestException(message)
