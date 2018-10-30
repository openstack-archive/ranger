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

import json
import urllib

from ranger_tempest_plugin.schemas import customers_schema as schema
from ranger_tempest_plugin.services import base_client

from tempest import config

CONF = config.CONF


class CmsClient(base_client.RangerClientBase):

    cms_url = '%s:%s' % (CONF.ranger.uri, CONF.ranger.cms_port)
    version = 'v1'

    # POST

    def create_customer(self, **kwargs):
        uri = '%s/%s/orm/customers' % (self.cms_url, self.version)
        post_body = json.dumps(kwargs)
        return self.post_request(uri, post_body, schema.create_customer)

    def add_default_user(self, customer_id, *args):
        uri = '%s/%s/orm/customers/%s/users' \
            % (self.cms_url, self.version, customer_id)
        post_body = json.dumps(args)
        return self.post_request(uri, post_body, schema.add_users)

    def add_regions(self, customer_id, regions):
        uri = '%s/%s/orm/customers/%s/regions' \
            % (self.cms_url, self.version, customer_id)
        post_body = json.dumps(regions)
        return self.post_request(uri, post_body, schema.add_regions)

    def add_region_user(self, customer_id, region_id, *args):
        uri = '%s/%s/orm/customers/%s/regions/%s/users' \
            % (self.cms_url, self.version, customer_id, region_id)
        post_body = json.dumps(args)
        return self.post_request(uri, post_body, schema.add_users)

    def add_metadata(self, customer_id, metadata):
        uri = '%s/%s/orm/customers/%s/metadata' \
            % (self.cms_url, self.version, customer_id)
        post_body = json.dumps(metadata)
        return self.post_request(uri, post_body, schema.add_metadata)

    # PUT

    def update_customer(self, customer_id, customer):
        uri = '%s/%s/orm/customers/%s' \
            % (self.cms_url, self.version, customer_id)
        put_body = json.dumps(customer)
        return self.put_request(uri, put_body, schema.update_customer)

    def enable_customer(self, customer_id, value):
        uri = '%s/%s/orm/customers/%s/enabled' \
            % (self.cms_url, self.version, customer_id)
        put_body = json.dumps({'enabled': value})
        return self.put_request(uri, put_body, schema.enable_customer)

    def replace_default_user(self, customer_id, *args):
        uri = '%s/%s/orm/customers/%s/users' \
            % (self.cms_url, self.version, customer_id)
        put_body = json.dumps(args)
        return self.put_request(uri, put_body, schema.replace_users)

    def replace_region_user(self, customer_id, region_id, *args):
        uri = '%s/%s/orm/customers/%s/regions/%s/users' \
            % (self.cms_url, self.version, customer_id, region_id)

        put_body = json.dumps(args)
        return self.put_request(uri, put_body, schema.replace_users)

    def replace_metadata(self, customer_id, metadata):
        uri = '%s/%s/orm/customers/%s/metadata' \
            % (self.cms_url, self.version, customer_id)
        put_body = json.dumps(metadata)
        return self.put_request(uri, put_body, schema.replace_metadata)

    # GET

    def get_customer(self, identifier):
        uri = '%s/%s/orm/customers/%s' \
            % (self.cms_url, self.version, identifier)
        return self.get_request(uri, schema.get_customer)

    def list_customers(self, filter=None):
        uri = '%s/%s/orm/customers' % (self.cms_url, self.version)
        if filter is not None:
            uri += '?' + urllib.urlencode(filter)
        return self.get_request(uri, schema.list_customer)

    # DELETE

    def delete_region_from_customer(self, customer_id, region_id):
        uri = '%s/%s/orm/customers/%s/regions/%s' % (
            self.cms_url, self.version, customer_id, region_id)
        return self.delete_request(uri, schema.delete_region_from_customer)

    def delete_customer(self, customer_id):
        uri = '%s/%s/orm/customers/%s' \
            % (self.cms_url, self.version, customer_id)
        return self.delete_request(uri, schema.delete_customer)

    def delete_default_user(self, customer_id, user_id):
        uri = '%s/%s/orm/customers/%s/users/%s' \
            % (self.cms_url, self.version, customer_id, user_id)
        return self.delete_request(uri, schema.delete_default_user)

    def delete_region_user(self, customer_id, region_id, user_id):
        uri = '%s/%s/orm/customers/%s/regions/%s/users/%s' \
            % (self.cms_url, self.version, customer_id, region_id, user_id)
        return self.delete_request(uri, schema.delete_user_from_region)
