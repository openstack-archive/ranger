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

_status = {
    'type': 'string',
    'enum': ['Success', 'no regions', 'Error', 'Pending', 'Submitted']
}

_links = {
    'type': 'object',
    'properties': {
        'self': {'type': 'string'}
    },
    'required': ['self']
}

_region = {
    'type': 'object',
    'properties': {
        'added': {'type': 'string'},
        'id': {'type': 'string'},
        'links': _links
    },
    'required': ['added', 'id', 'links']
}

_group = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'links': _links,
        'created': {'type': 'string', 'format': 'date-time'}
    },
    'required': ['id', 'links', 'created']
}

create_group = {
    'status_code': [201],
    'response_body': {
        'type': 'object',
        'properties': {
            'group': _group,
            'transaction_id': {'type': 'string'}
        },
        'required': ['group', 'transaction_id']
    }
}

get_group = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'status': _status,
            'uuid': {'type': 'string'},
            'enabled': {'type': 'boolean'},
            'domain_name': {'type': 'string'},
            'name': {'type': 'string'},
            'regions': {'type': 'array'},
            'description': {'type': 'string'}
        },
        'required': ['status', 'uuid', 'enabled', 'domain_name', 'name',
                     'regions', 'description']
    }
}

list_groups = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'groups': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'status': _status,
                        'description': {'type': 'string'},
                        'enabled': {'type': 'boolean'},
                        'domain_name': {'type': 'string'},
                        'regions': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        },
                        'id': {'type': 'string'},
                        'name': {'type': 'string'}
                    },
                    'required': ['status', 'description', 'enabled',
                                 'domain_name', 'regions', 'id', 'name']
                }
            }
        },
        'required': ['groups']
    }
}

delete_group = {
    'status_code': [204]
}

delete_region_from_group = delete_group
