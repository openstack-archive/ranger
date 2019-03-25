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
import requests
from tempest import config
from tempest.lib import auth
from tempest.lib.common import rest_client

CONF = config.CONF


class ResponseError(Exception):
    pass


class ConnectionError(Exception):
    pass


class RangerClientBase(rest_client.RestClient):

    rms_url = CONF.ranger.RANGER_RMS_BASE_URL
    auth_region = CONF.identity.region
    timeout = 10

    # def get_keystone_ep(rms_url, region_name):
    def get_keystone_ep(self, rms_url, region_name):
        """Get the Keystone EP from RMS.

        :param rms_url: RMS server URL
        :param region_name: The region name
        :return: Keystone EP (string), None if it was not found
        """
        try:
            response = requests.get('%s/v2/orm/regions?regionname=%s' % (
                rms_url, region_name, ), verify=CONF.ranger.verify)
        except requests.exceptions.ConnectionError as e:
            print('Could not connect to RMS, URL: {}'.format(rms_url))
            return None

        if response.status_code != 200:
            print('RMS returned status: {}, content: {}'.format(
                response.status_code, response.content))
            return None

        # get the identity URL info from the rms region record
        lcp = response.json()
        try:
            for endpoint in lcp['regions'][0]['endpoints']:
                if endpoint['type'] == 'identity':
                    return endpoint['publicURL']
        except KeyError:
            print('Key error while attempting to get keystone endpoint. '
                  'Please investigate.')
            return None

        # Keystone EP not found in the response
        print('No identity endpoint was found in the response from RMS')
        return None

    def get_token(self, timeout, host):
        headers = {
            'Content-Type': 'application/json',
        }
        url = '%s/v3/auth/tokens'
        data = '''
{
   "auth":{
      "identity":{
         "methods":[
            "password"
         ],
         "password":{
            "user":{
               "domain":{
                  "name":"%s"
               },
               "name":"%s",
               "password":"%s"
            }
         }
      },
      "scope":{
         "project":{
            "name":"%s",
            "domain":{
               "name":"%s"
            }
         }
      }
   }
}'''
        # import pdb; pdb.set_trace()
        if not CONF.ranger.auth_enabled:
            return None

        region = self.auth_region

        keystone_ep = self.get_keystone_ep('{}'.format(host), region)
        if keystone_ep is None:
            raise ConnectionError(
                'Failed in get_token, host: {}, region: {}'.format(host,
                                                                   region))

        url = url % (keystone_ep,)
        data = data % (CONF.auth.admin_domain_name,
                       CONF.auth.admin_username,
                       CONF.auth.admin_password,
                       CONF.auth.admin_project_name,
                       CONF.auth.admin_domain_name,)

        try:
            resp = requests.post(url, timeout=timeout, data=data, headers=headers)
            if resp.status_code != 201:
                raise ResponseError(
                    'Failed to get token (Reason: {})'.format(
                        resp.status_code))
            return resp.headers['x-subject-token']

        except Exception as e:
            print e.message
            raise ConnectionError(e.message)

    def get_headers(self):
        headers = {'X-Auth-Region': CONF.identity.region,
                   'X-Auth-Token': self.get_token(self.timeout, self.rms_url),
                   'X-RANGER-Tracking-Id': 'test',
                   'X-RANGER-Requester': CONF.auth.admin_username,
                   'X-RANGER-Client': 'cli',
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


class RangerAuthProvider(auth.KeystoneV3AuthProvider):

    def __init__(self, credentials, auth_url=CONF.identity.uri_v3):
        super(RangerAuthProvider, self).__init__(credentials, auth_url)

    def auth_request(self, method, url, headers=None, body=None, filters=None):
        filters = {'service': 'identity'}
        auth_headers = super(RangerAuthProvider,
                             self).auth_request(method,
                                                url,
                                                filters=filters)

        base_headers = auth_headers[1]
        base_headers.update(headers)
        auth_req = dict(url=url, headers=base_headers, body=body)
        return auth_req['url'], auth_req['headers'], auth_req['body']
