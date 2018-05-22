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

from aic_orm_tempest_plugin import clients

from oslo_log import log as logging
import six
from tempest import config
from tempest import test

CONF = config.CONF
LOG = logging.getLogger(__name__)


class BaseOrmTest(test.BaseTestCase):

    credentials = ['admin', 'primary', 'alt']

    client_manager = clients.OrmClientManager

    build_timeout = 120
    build_interval = 10

    @classmethod
    def setup_clients(cls):
        super(BaseOrmTest, cls).setup_clients()
        cls.identity_client = cls.os_admin.tenants_client

    @classmethod
    def skip_checks(cls):
        super(BaseOrmTest, cls).skip_checks()
        if not CONF.service_available.orm:
            skip_msg = ("%s skipped as orm is not available" % cls.__name__)
            raise cls.skipException(skip_msg)

    def assertExpected(self, expected, actual, excluded_keys):
        for key, value in six.iteritems(expected):
            if key not in excluded_keys:
                self.assertIn(key, actual)
                self.assertEqual(value, actual[key], key)
