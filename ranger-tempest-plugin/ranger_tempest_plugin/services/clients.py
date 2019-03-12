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

from ranger_tempest_plugin.services import base_client
from ranger_tempest_plugin.services.cms_client import CmsClient
from ranger_tempest_plugin.services.fms_client import FmsClient
from ranger_tempest_plugin.services.ims_client import ImsClient
from ranger_tempest_plugin.services.rms_client import RmsClient

from tempest import clients
from tempest import config

CONF = config.CONF


class OrmClientManager(clients.Manager):

    def __init__(self, credentials=None):
        super(OrmClientManager, self).__init__(credentials)
        self.cms_client = CmsClient(base_client.RangerAuthProvider(credentials),
                                     CONF.identity.catalog_type,
				     CONF.identity.region,
                                     CONF.ranger.RANGER_CMS_BASE_URL)
        self.fms_client = FmsClient(base_client.RangerAuthProvider(credentials),
                                     CONF.identity.catalog_type,
                                     CONF.identity.region,
                                     CONF.ranger.RANGER_FMS_BASE_URL)
        self.rms_client = RmsClient(base_client.RangerAuthProvider(credentials),
                                     CONF.identity.catalog_type,
                                     CONF.identity.region,
                                     CONF.ranger.RANGER_IMS_BASE_URL)
        self.ims_client = ImsClient(base_client.RangerAuthProvider(credentials),
                                     CONF.identity.catalog_type,
                                     CONF.identity.region,
                                     CONF.ranger.RANGER_RMS_BASE_URL)
        self.cms_client = CmsClient(base_client.RangerAuthProvider(credentials),
                                    CONF.identity.catalog_type,
                                    CONF.identity.region,
                                    CONF.ranger.uri)
        self.fms_client = FmsClient(base_client.RangerAuthProvider(credentials),
                                    CONF.identity.catalog_type,
                                    CONF.identity.region,
                                    CONF.ranger.uri)
        self.rms_client = RmsClient(base_client.RangerAuthProvider(credentials),
                                    CONF.identity.catalog_type,
                                    CONF.identity.region,
                                    CONF.ranger.uri)
        self.ims_client = ImsClient(base_client.RangerAuthProvider(credentials),
                                    CONF.identity.catalog_type,
                                    CONF.identity.region,
                                    CONF.ranger.uri)
