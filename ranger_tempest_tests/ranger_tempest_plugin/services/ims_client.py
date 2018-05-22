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

from ranger_tempest_plugin.schemas import images_schema as schema
from ranger_tempest_plugin.services import base_client
from tempest import config

CONF = config.CONF


class ImsClient(base_client.OrmClientBase):

    ims_url = '%s:%s' % (CONF.orm.uri, CONF.orm.ims_port)
    version = "v1"

    def get_headers(self):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'X-Auth-Region': CONF.identity.region,
                   'X-RANGER-Tracking-Id': 'test',
                   'X-RANGER-Requester': CONF.auth.admin_username,
                   'X-RANGER-Client': 'cli'
                   }
        return headers

    def create_image(self, **kwargs):
        uri = '%s/%s/orm/images' % (self.ims_url, self.version)
        post_body = {"image": kwargs}
        post_body = json.dumps(post_body)
        return self.post_request(uri, post_body, schema.create_image)

    def update_image(self, image_id, para=None, **kwargs):
        if para is None:
            uri = '%s/%s/orm/images/%s' % (
                self.ims_url, self.version, image_id)
        else:
            uri = '%s/%s/orm/images/%s/%s' % (
                self.ims_url, self.version, image_id, para)
        put_body = {"image": kwargs}
        put_body = json.dumps(put_body)
        return self.put_request(uri, put_body, schema.update_image)

    def get_image(self, identifier, para=None):
        if para is None:
            uri = '%s/%s/orm/images/%s' % (self.ims_url, self.version,
                                           identifier)
        else:
            uri = '%s/%s/orm/images/%s/%s' % (self.ims_url, self.version,
                                              identifier, para)
        return self.get_request(uri, schema.get_image)

    def list_images(self, para=None):
        if para is None:
            uri = '%s/%s/orm/images' % (self.ims_url, self.version)
        else:
            uri = '%s/%s/orm/images/%s' % (self.ims_url, self.version, para)
        return self.get_request(uri, schema.list_images)

    def enabled_image(self, image_id, bool):
        uri = '%s/%s/orm/images/%s/enabled' \
            % (self.ims_url, self.version, image_id)
        put_body = json.dumps({'enabled': bool})
        return self.put_request(uri, put_body, schema.enable_image_resp)

    def add_region_to_image(self, image_id, region_id):
        uri = '%s/%s/orm/images/%s/regions/' % (self.ims_url,
                                                self.version, image_id)
        post_body = json.dumps({"regions": [{"name": region_id}]})
        return self.post_request(uri, post_body, schema.add_region)

    def delete_region_from_image(self, image_id, region_id):
        uri = '%s/%s/orm/images/%s/regions/%s' % (self.ims_url,
                                                  self.version, image_id,
                                                  region_id)
        return self.delete_request(uri, schema.delete_region)

    def delete_image(self, image_id):
        uri = '%s/%s/orm/images/%s' % (self.ims_url, self.version, image_id)
        return self.delete_request(uri, schema.delete_image)

    def add_customer_to_image(self, image_id, tenant_id):
        uri = '%s/%s/orm/images/%s/customers' % (
            self.ims_url, self.version, image_id)
        post_body = json.dumps({"customers": [tenant_id]})
        return self.post_request(uri, post_body, schema.add_tenant_to_image)

    def update_customer(self, image_id, tenant_id):
        uri = '%s/%s/orm/images/%s/customers' % (self.ims_url, self.version,
                                                 image_id)
        put_body = json.dumps({"customers": [tenant_id]})
        return self.put_request(uri, put_body, schema.update_tenant)

    def delete_customer_from_image(self, image_id, tenant_id):
        uri = '%s/%s/orm/images/%s/customers/%s' % (self.ims_url,
                                                    self.version,
                                                    image_id,
                                                    tenant_id)
        return self.delete_request(uri, schema.delete_tenant_from_image)
