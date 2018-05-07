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

import random

from oslo_log import log as logging
from tempest import config
from tempest.lib.common.utils import data_utils

LOG = logging.getLogger(__name__)
CONF = config.CONF


def rand_region_status(exclude=[]):
    statuses = {'functional', 'maintenance', 'down', 'building'}.difference(
        exclude)
    return random.choice(list(statuses))


def rand_region_metadata():
    metadata = {}
    for i in range(random.randint(2, 10)):
        metadata[data_utils.rand_name()] = [data_utils.arbitrary_string()]
    return metadata


def rand_region(id=None):
    if id is None:
        id = data_utils.rand_name()
    region_dict = {
        'status': rand_region_status(),
        'id': id,
        'name': id,
        'designType': data_utils.arbitrary_string(),
        'locationType': data_utils.arbitrary_string(),
        'vlcpName': data_utils.arbitrary_string(),
        'description': data_utils.arbitrary_string(),
        'rangerAgentVersion': data_utils.arbitrary_string(),
        'OSVersion': data_utils.arbitrary_string(),
        'CLLI': data_utils.arbitrary_string(),
        'address': {
            'country': data_utils.arbitrary_string(),
            'state': data_utils.arbitrary_string(),
            'city': data_utils.arbitrary_string(),
            'street': data_utils.arbitrary_string(),
            'zip': str(data_utils.rand_int_id(start=10000, end=99999))
        },
        'metadata': {
            data_utils.rand_name(): [data_utils.arbitrary_string()],
            data_utils.rand_name(): [data_utils.arbitrary_string()]
        },
        'endpoints': [{
            'publicURL': data_utils.rand_url(),
            'type': 'dashboard'
        }, {
            'publicURL': data_utils.rand_url(),
            'type': 'identity'
        }, {
            'publicURL': data_utils.rand_url(),
            'type': 'ord'
        }]
    }
    return region_dict


def rand_region_group(region_ids, id=None):
    if id is None:
        id = data_utils.rand_name()
    group_dict = {
        'name': id,
        'id': id,
        'description': data_utils.arbitrary_string(),
        'regions': region_ids
    }

    return group_dict
