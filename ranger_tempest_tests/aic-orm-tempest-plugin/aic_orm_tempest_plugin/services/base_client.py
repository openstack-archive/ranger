# Copyright 2015
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

from tempest import config
from tempest.lib import auth
from tempest.lib.common import rest_client

CONF = config.CONF


class OrmClientBase(rest_client.RestClient):

    def get_headers(self):
        headers = {'X-Auth-Region': CONF.identity.region,
                   'X-AIC-ORM-Tracking-Id': 'test',
                   'X-AIC-ORM-Requester': CONF.auth.admin_username,
                   'X-AIC-ORM-Client': 'cli',
                   'Content-Type': 'application/json'
                   }
        return headers

    def get_request(self, uri, expected_body_schema):
        ex_headers = self.get_headers()
        resp, body = self.get(uri, extra_headers=ex_headers)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        self.validate_response(expected_body_schema, resp, body)
        return resp, body

    def put_request(self, uri, put_body, expected_body_schema):
        ex_headers = self.get_headers()
        resp, body = self.put(uri, body=put_body, extra_headers=ex_headers)
        self.expected_success([200, 201], resp.status)
        body = json.loads(body)
        self.validate_response(expected_body_schema, resp, body)
        return resp, body

    def delete_request(self, uri, expected_body_schema):
        ex_headers = self.get_headers()
        resp, body = self.delete(uri, extra_headers=ex_headers)
        self.expected_success(204, resp.status)
        self.validate_response(expected_body_schema, resp, body)
        return resp, body

    def post_request(self, uri, post_body, expected_body_schema):
        ex_headers = self.get_headers()
        resp, body = self.post(uri, body=post_body,
                               extra_headers=ex_headers)
        self.expected_success([200, 201], resp.status)
        body = json.loads(body)
        self.validate_response(expected_body_schema, resp, body)
        return resp, body


class OrmAuthProvider(auth.KeystoneV2AuthProvider):

    def __init__(self, credentials, auth_url=CONF.identity.uri):
        super(OrmAuthProvider, self).__init__(credentials, auth_url)

    def auth_request(self, method, url, headers=None, body=None, filters=None):
        filters = {'service': 'identity'}
        auth_headers = super(OrmAuthProvider,
                             self).auth_request(method,
                                                url,
                                                filters=filters)
        base_headers = auth_headers[1]
        base_headers.update(headers)
        auth_req = dict(url=url, headers=base_headers, body=body)
        return auth_req['url'], auth_req['headers'], auth_req['body']
