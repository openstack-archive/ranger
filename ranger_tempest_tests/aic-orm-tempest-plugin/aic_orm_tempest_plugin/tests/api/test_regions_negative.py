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

from aic_orm_tempest_plugin.tests.api import base

from tempest import config

CONF = config.CONF


class TestTempestRegionsNegative(base.BaseOrmTest):

    @classmethod
    def setup_credentials(cls):
        super(TestTempestRegionsNegative, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(TestTempestRegionsNegative, cls).setup_clients()
        cls.client = cls.rmsclient

    @classmethod
    def resource_setup(cls):
        cls.set_role_to_admin()
        super(TestTempestRegionsNegative, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        cls.delete_role_to_admin()
        super(TestTempestRegionsNegative, cls).resource_cleanup()
