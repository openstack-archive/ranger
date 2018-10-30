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
import urllib

from ranger_tempest_plugin.schemas import regions_schema as schema
from ranger_tempest_plugin.services import base_client

from tempest import config


CONF = config.CONF


class RmsClient(base_client.RangerClientBase):

    rms_url = '%s:%s' % (CONF.ranger.uri, CONF.ranger.region_port)
    version = "v2"

    def create_region(self, region_id, **kwargs):
        uri = '%s/%s/orm/regions' % (self.rms_url, self.version)
        post_body = {
            'status': 'functional',
            'name': region_id,
            'id': region_id,
            'description': region_id,
            'designType': 'compact',
            'locationType': 'testlocation',
            'vlcpName': 'testvlcp',
            'address': {
                'country': 'usa',
                'state': 'tx',
                'city': 'austin',
                'street': '12 main',
                'zip': '12345'
            },
            'metadata': {
                'key': ["value"]
            },
            'endpoints': [
                {
                    'publicURL':
                        'https://dashboard-ranger.%s.com' % region_id,
                    'type': 'dashboard'
                },
                {
                    'publicURL':
                        'https://identity-ranger.%s.com:5000' % region_id,
                    'type': 'identity'
                },
                {
                    'publicURL':
                        'https://ranger-agent.%s.com:9010' % region_id,
                    'type': 'ord'
                },

            ],
            'rangerAgentVersion': '3.6',
            'OSVersion': 'kilo',
            'CLLI': 'testclli'
        }
        if kwargs is not None:
            for key in kwargs:
                post_body[key] = kwargs[key]

        post_body = json.dumps(post_body)
        return self.post_request(uri, post_body, schema.create_region)

    def update_region(self, region_id, **kwargs):
        uri = '%s/%s/orm/regions/%s' % (self.rms_url, self.version, region_id)
        put_body = json.dumps(kwargs)
        return self.put_request(uri, put_body, schema.update_region)

    def update_region_status(self, region_id, status):
        uri = '%s/%s/orm/regions/%s/status' \
            % (self.rms_url, self.version, region_id)
        put_body = json.dumps(status)
        return self.put_request(uri, put_body, schema.update_status)

    def update_region_metadata(self, region_id, metadata):
        uri = '%s/%s/orm/regions/%s/metadata' \
            % (self.rms_url, self.version, region_id)
        put_body = json.dumps(metadata)
        return self.put_request(uri, put_body, schema.update_metadata)

    def get_region(self, identifier):
        uri = '%s/%s/orm/regions/%s' % (self.rms_url, self.version, identifier)
        return self.get_request(uri, schema.get_region)

    def get_region_metadata(self, identifier):
        uri = '%s/%s/orm/regions/%s/metadata'\
            % (self.rms_url, self.version, identifier)
        return self.get_request(uri, schema.get_region_metadata)

    def list_regions_v1(self):
        uri = self.rms_url + '/lcp'
        return self.get_request(uri, schema.list_region_v1)

    def list_regions(self, filter=None):
        uri = '%s/%s/orm/regions' % (self.rms_url, self.version)
        if filter is not None:
            uri += '?' + urllib.urlencode(filter)
        return self.get_request(uri, schema.list_region)

    def delete_region(self, region_id):
        uri = '%s/%s/orm/regions/%s' % (self.rms_url, self.version, region_id)
        return self.delete_request(uri, schema.delete_region)

    def add_region_metadata(self, region_id, **kwargs):
        uri = '%s/%s/orm/regions/%s/metadata'\
            % (self.rms_url, self.version, region_id)
        post_body = json.dumps(kwargs)
        return self.post_request(uri, post_body, schema.update_metadata)
#
#    def delete_region_metadata(self, region_id, key):
#        uri = '%s/%s/orm/regions/%s/metadata/%s' % (
#            self.rms_url, self.version, region_id, key)
#        ex_headers = self.get_headers()
#        resp, body = self.delete(uri, extra_headers=ex_headers)
#        self.expected_success(200, resp.status)
#        body = json.loads(body)
#        return rest_client.ResponseBody(resp, body)

    def create_region_group(self, **kwargs):
        uri = '%s/%s/orm/groups' % (self.rms_url, self.version)
        post_body = json.dumps(kwargs)
        return self.post_request(uri, post_body, schema.create_region_group)

    def update_region_group(self, group_id, **kwargs):
        uri = '%s/%s/orm/groups/%s' % (self.rms_url, self.version, group_id)
        put_body = json.dumps(kwargs)
        return self.put_request(uri, put_body, schema.update_region_group)

    def get_region_group(self, identifier):
        uri = '%s/%s/orm/groups/%s'\
            % (self.rms_url, self.version, identifier)
        return self.get_request(uri, schema.get_region_group)

    def list_region_groups(self):
        uri = '%s/%s/orm/groups' % (self.rms_url, self.version)
        return self.get_request(uri, schema.list_region_groups)

    def delete_region_group(self, region_group_id):
        uri = '%s/%s/orm/groups/%s' % (self.rms_url, self.version,
                                       region_group_id)
        return self.delete_request(uri, schema.delete_region_group)
