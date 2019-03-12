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

from ranger_tempest_plugin.schemas import flavors_schema as schema
from ranger_tempest_plugin.services import base_client

from tempest import config
from tempest.lib.common import rest_client

CONF = config.CONF


class FmsClient(base_client.RangerClientBase):

    fms_url = CONF.ranger.RANGER_FMS_BASE_URL
    version = "v1"

    def get_extra_headers(self):
        headers = {'X-Auth-Region': CONF.identity.region,
                   'X-RANGER-Tracking-Id': 'test',
                   'X-RANGER-Requester': CONF.auth.admin_username,
                   'X-RANGER-Client': 'cli'
                   }
        return headers

    def create_flavor(self, **kwargs):
        uri = '%s/%s/orm/flavors' % (self.fms_url, self.version)
        post_body = {"flavor": kwargs}
        post_body = json.dumps(post_body)
        # ex_headers = self.get_headers()
        # resp, body = self.post(uri, body=post_body,
        #                       extra_headers=ex_headers)
        # body = json.loads(body)
        # self.validate_response(schema.create_flavor, resp, body)
        # return rest_client.ResponseBody(resp, body["flavor"])
        return self.post_request(uri, post_body, schema.create_flavor)

    def get_flavor(self, identifier, para=None):
        if para is None:
            uri = '%s/%s/orm/flavors/%s' % (self.fms_url, self.version,
                                            identifier)
        else:
            uri = '%s/%s/orm/flavors/%s/%s' % (self.fms_url, self.version,
                                               identifier, para)
        return self.get_request(uri, schema.get_flavor)

    def list_flavors(self, para=None):
        if para is None:
            uri = '%s/%s/orm/flavors' % (self.fms_url, self.version)
        else:
            uri = '%s/%s/orm/flavors/%s' % (self.fms_url, self.version, para)
        # ex_headers = self.get_headers()
        # resp, body = self.get(url, extra_headers=ex_headers)
        # self.expected_success(200, resp.status)
        # body = json.loads(body)
        # self.validate_response(schema.list_flavors, resp, body)
        # return rest_client.ResponseBody(resp, body)
        return self.get_request(uri, schema.list_flavors)

    def delete_region_from_flavor(self, flavor_id, region_id):
        uri = '%s/%s/orm/flavors/%s/regions/%s' % (self.fms_url,
                                                   self.version, flavor_id,
                                                   region_id)
        ex_headers = self.get_headers()
        resp, body = self.delete(uri, extra_headers=ex_headers)
        self.expected_success(204, resp.status)
        return rest_client.ResponseBody(resp, body)

    def delete_flavor(self, flavor_id):
        uri = '%s/%s/orm/flavors/%s' %\
            (self.fms_url, self.version, flavor_id)
        return self.delete_request(uri, schema.delete_flavor)

    def delete_tags(self, flavor_id, para):
        if para is None:
            uri = '%s/%s/orm/flavors/%s/tags' % (self.fms_url, self.version,
                                                 flavor_id)
        else:
            uri = '%s/%s/orm/flavors/%s/tags/%s' % (self.fms_url, self.version,
                                                    flavor_id, para)
        return self.delete_request(uri, schema.delete_tags)

    def get_tags(self, flavor_id):
        uri = '%s/%s/orm/flavors/%s/tags' % (self.fms_url, self.version,
                                             flavor_id)
        return self.get_request(uri, schema.get_tags)

    def add_tags(self, flavor_id, tag_body):
        uri = '%s/%s/orm/flavors/%s/tags' % (self.fms_url, self.version,
                                             flavor_id)
        post_body = json.dumps(tag_body)
        return self.post_request(uri, post_body, schema.add_tags)

    def update_tags(self, flavor_id, tag_body):
        uri = '%s/%s/orm/flavors/%s/tags' % (self.fms_url, self.version,
                                             flavor_id)
        put_body = json.dumps(tag_body)
        return self.put_request(uri, put_body, schema.update_tags)

    def get_extra_specs(self, flavor_id):
        uri = '%s/%s/orm/flavors/%s/os_extra_specs' % (self.fms_url,
                                                       self.version,
                                                       flavor_id)
        return self.get_request(uri, schema.get_extra_specs)

    def add_flvr_tenants(self, flavor_id, tenant_body):
        uri = '%s/%s/orm/flavors/%s/tenants/' % (self.fms_url,
                                                 self.version,
                                                 flavor_id)
        post_body = json.dumps(tenant_body)
        return self.post_request(uri, post_body, schema.add_tenant)

    def add_flvr_regions(self, flavor_id, region_body):
        uri = '%s/%s/orm/flavors/%s/regions' % (self.fms_url,
                                                self.version,
                                                flavor_id)
        post_body = json.dumps(region_body)
        return self.post_request(uri, post_body, schema.add_region)

    def delete_flvr_region(self, flavor_id, region_id):
        uri = '%s/%s/orm/flavors/%s/regions/%s' % (self.fms_url,
                                                   self.version,
                                                   flavor_id, region_id)
        return self.delete_request(uri, schema.delete_region)

    def add_extra_specs(self, flavor_id, extra_specs_body):
        uri = '%s/%s/orm/flavors/%s/os_extra_specs' % (self.fms_url,
                                                       self.version,
                                                       flavor_id)
        post_body = json.dumps(extra_specs_body)
        return self.post_request(uri, post_body, schema.add_extra_specs)

    def update_extra_specs(self, flavor_id, extra_specs_body):
        uri = '%s/%s/orm/flavors/%s/os_extra_specs' % (self.fms_url,
                                                       self.version,
                                                       flavor_id)
        put_body = json.dumps(extra_specs_body)
        return self.put_request(uri, put_body, schema.update_extra_specs)

    def delete_extra_specs(self, flavor_id, para):
        if para is None:
            uri = '%s/%s/orm/flavors/%s/os_extra_specs' % (self.fms_url,
                                                           self.version,
                                                           flavor_id)
        else:
            uri = '%s/%s/orm/flavors/%s/os_extra_specs/%s' % (self.fms_url,
                                                              self.version,
                                                              flavor_id, para)
        return self.delete_request(uri, schema.delete_extra_specs)

    def delete_flvr_tenant(self, flavor_id, tenant):
        uri = '%s/%s/orm/flavors/%s/tenants/%s' % (self.fms_url,
                                                   self.version,
                                                   flavor_id, tenant)
        return self.delete_request(uri, schema.delete_tenant)
