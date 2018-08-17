# Copyright 2017
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
#    under the License

_metadata = {
    'type': 'object',
    'items': {
        'type': 'array',
        'items': {'type': 'string'}
    }
}

_region = {
    'type': 'object',
    'properties': {
        'status': {'type': 'string'},
        'endpoints': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'publicURL': {'type': 'string'},
                    'type': {'type': 'string'}
                },
                'required': ['publicURL', 'type']
            }
        },
        'CLLI': {'type': 'string'},
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'designType': {'type': 'string'},
        'locationType': {'type': 'string'},
        'vlcpName': {'type': 'string'},
        'address': {
            'type': 'object',
            'properties': {
                'country': {'type': 'string'},
                'state': {'type': 'string'},
                'street': {'type': 'string'},
                'zip': {'type': 'string'},
                'city': {'type': 'string'},
            },
            'required': ['country', 'state', 'street', 'zip', 'city']
        },
        'rangerAgentVersion': {'type': 'string'},
        'OSVersion': {'type': 'string'},
        'id': {'type': 'string'},
        'metadata': _metadata,
        'created': {'type': 'string', 'format': 'date-time'},
        'modified': {'type': 'string', 'format': 'date-time'}
    },
    'required': ['status', 'endpoints', 'rangerAgentVersion', 'OSVersion',
                 'CLLI', 'created', 'modified', 'metadata', 'address',
                 'locationType', 'designType', 'description', 'name', 'id',
                 'vlcpName']
}

get_region = {
    'status_code': [200],
    'response_body': _region
}

get_region_metadata = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {'metadata': _metadata},
        'required': ['metadata']
    }
}

create_region = {
    'status_code': [201],
    'response_body': _region
}

update_region = create_region

update_metadata = {
    'status_code': [201],
    'response_body': {
        'type': 'object',
        'properties': {'metadata': _metadata},
        'required': ['metadata']
    }
}

update_status = {
    'status_code': [201],
    'response_body': {
        'type': 'object',
        'properties': {
            'status': {'type': 'string'},
            'links': {
                'type': 'object',
                'properties': {
                    'self': {'type': 'string'}
                }
            }
        },
        'required': ['status', 'links']
    }
}

delete_region = {
    'status_code': [204]
}

list_region = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'regions': {
                'type': 'array',
                'items': _region
            }
        },
        'required': ['regions']
    }
}

list_region_v1 = {
    'status_code': [200],
    'response_body': {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'status': {'type': 'string'},
                'vLCP_name': {'type': 'string'},
                'ORD_EP': {'type': 'string'},
                'horizon_EP': {'type': 'string'},
                'design_type': {'type': 'string'},
                'rangerAgentVersion': {'type': 'string'},
                'id': {'type': 'string'},
                'OS_version': {'type': 'string'},
                'keystone_EP': {'type': 'string'},
                'zone_name': {'type': 'string'},
                'location_type': {'type': 'string'}
            }
        }
    }
}

_region_group = {
    'type': 'object',
    'properties': {
        'description': {'type': 'string'},
        'links': {
            'type': 'object',
            'properties': {'self': {'type': 'string'}}
        },
        'created': {'type': 'string', 'format': 'date-time'},
        'modified': {'type': 'string', 'format': 'date-time'},
        'id': {'type': 'string'},
        'name': {'type': 'string'}
    },
    'required': ['description', 'created', 'modified', 'id', 'name']
}

create_region_group = {
    'status_code': [201],
    'response_body': {
        'type': 'object',
        'properties': {
            'group': _region_group
        },
        'required': ['group']
    }
}

update_region_group = create_region_group

get_region_group = {
    'status_code': [200],
    'response_body': _region_group
}

list_region_groups = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'groups': {
                'type': 'array',
                'items': _region_group
            }
        },
        'required': ['groups']
    }
}

delete_region_group = {
    'status_code': [204]
}
