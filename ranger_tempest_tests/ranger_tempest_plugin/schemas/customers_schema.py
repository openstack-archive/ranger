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

_user = {
    'type': 'object',
    'properties': {
        'added': {'type': 'string', 'format': 'date-time'},
        'id': {'type': 'string'},
        'links': _links
    },
    'required': ['added', 'id', 'links']
}

_customer = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'links': _links,
        'created': {'type': 'string', 'format': 'date-time'}
    },
    'required': ['id', 'links', 'created']
}

create_customer = {
    'status_code': [201],
    'response_body': {
        'type': 'object',
        'properties': {
            'customer': _customer,
            'transaction_id': {'type': 'string'}
        },
        'required': ['customer', 'transaction_id']
    }
}

update_customer = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'customer': _customer,
            'transaction_id': {'type': 'string'}
        },
        'required': ['customer', 'transaction_id']
    }
}

add_regions = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'regions': {
                'type': 'array',
                'items': _region
            },
            'transaction_id': {'type': 'string'}
        },
        'required': ['regions', 'transaction_id']
    }
}

add_users = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'users': {
                'type': 'array',
                'items': _user
            },
            'transaction_id': {'type': 'string'}
        },
        'required': ['users', 'transaction_id']
    }
}

replace_users = add_users

add_metadata = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'customer': _customer,
            'transaction_id': {'type': 'string'}
        },
        'required': ['customer', 'transaction_id']
    }
}

replace_metadata = add_metadata

enable_customer = add_metadata

get_customer = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'status': _status,
            'uuid': {'type': 'string'},
            'users': {'type': 'array'},
            'description': {'type': 'string'},
            'enabled': {'type': 'boolean'},
            'defaultQuotas': {'type': 'array'},
            'name': {'type': 'string'},
            'regions': {'type': 'array'},
            'custId': {'type': 'string'},
            'metadata': {'type': 'object'}
        },
        'required': ['status', 'uuid', 'users', 'description', 'enabled',
                     'defaultQuotas', 'name', 'regions', 'custId', 'metadata']
    }
}

list_customer = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'customers': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'status': _status,
                        'description': {'type': 'string'},
                        'enabled': {'type': 'boolean'},
                        'num_regions': {'type': 'integer'},
                        'regions': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        },
                        'id': {'type': 'string'},
                        'name': {'type': 'string'}
                    },
                    'required': ['status', 'description', 'enabled',
                                 'num_regions', 'regions', 'id', 'name']
                }
            }
        },
        'required': ['customers']
    }
}

delete_customer = {
    'status_code': [204]
}

delete_region_from_customer = delete_customer

delete_default_user = delete_customer

delete_user_from_region = delete_customer
