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

from ranger_tempest_plugin.schemas import group_schema as schema
from ranger_tempest_plugin.services import base_client

from tempest import config

CONF = config.CONF


class GrpClient(base_client.RangerClientBase):

    cms_url = CONF.ranger.RANGER_CMS_BASE_URL
    version = 'v1'

    def create_group(self, **kwargs):
        uri = '%s/%s/orm/groups' % (self.cms_url, self.version)
        post_body = json.dumps(kwargs)
        return self.post_request(uri, post_body, schema.create_group)

    def get_group(self, identifier):
        uri = '%s/%s/orm/groups/%s' \
            % (self.cms_url, self.version, identifier)
        return self.get_request(uri, schema.get_group)

    def list_groups(self, filter=None):
        uri = '%s/%s/orm/groups' % (self.cms_url, self.version)
        if filter is not None:
            uri += '?' + urllib.urlencode(filter)
        return self.get_request(uri, schema.list_groups)

    def delete_region_from_group(self, group_id, region_id):
        uri = '%s/%s/orm/groups/%s/regions/%s' % (
            self.cms_url, self.version, group_id, region_id)
        return self.delete_request(uri, schema.delete_region_from_group)

    def delete_group(self, group_id):
        uri = '%s/%s/orm/groups/%s' \
            % (self.cms_url, self.version, group_id)
        return self.delete_request(uri, schema.delete_group)
