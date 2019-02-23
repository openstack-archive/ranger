# Copyright 2017
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
#    under the License

_regions = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "type": {"type": "string"},
            "name": {"type": "string"},
            "error_message": {"type": "string"}
        }
    },
    "required": ["status", "type", "name"]
}

_extra_specs = {
    "type": "object",
    "additionalProperties": {
        "type": "string"
    }
}

_tags = {
    "type": "object",
    "items": {
        "type": "array",
        "items": {"type": "string"}
    }
}

_tenants = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

_flavor = {
    "type": "object",
    "properties": {
        "flavor": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "alias": {"type": "string"},
                "description": {"type": "string"},
                "tags": _tags,
                "series": {"type": "string"},
                "extra-specs": _extra_specs,
                "ram": {
                    "type": "string",
                    "pattern": "^[0-9]+$"
                },
                "ephemeral": {
                    "type": "string",
                    "pattern": "^[0-9]+$"
                },
                "visibility": {
                    "type": "string",
                    "enum": ["public", "private"]
                },
                "options": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "string"
                    }
                },
                "regions": _regions,
                "vcpus": {
                    "type": "string",
                    "pattern": "^[0-9]+$"
                },
                "swap": {
                    "type": "string",
                    "pattern": "^[0-9]+$"
                },
                "disk": {
                    "type": "string",
                    "pattern": "^[0-9]+$"
                },
                "tenants": _tenants,
                "id": {"type": "string"},
                "name": {"type": "string"}
            },
            "required": ["status", "series", "extra-specs",
                         "ram", "ephemeral", "visibility", "vcpus",
                         "regions", "swap", "disk", "tenants",
                         "id", "name"]
        }
    },
    "required": ["flavor"]
}

create_flavor = {
    "status_code": [201],
    "response_body": _flavor
}

get_flavor = {
    "status_code": [200],
    "response_body": _flavor
}

delete_flavor = {
    "status_code": [204]
}

list_flavors = {
    "status_code": [200],
    "response_body": {
        "type": "object",
        "properties": {
            "flavors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "description": {"type": "string"},
                        "tags": _tags,
                        "series": {"type": "string"},
                        "extra-specs": _extra_specs,
                        "ram": {
                            "type": "string",
                            "pattern": "^[0-9]+$"
                        },
                        "ephemeral": {
                            "type": "string",
                            "pattern": "^[0-9]+$"
                        },
                        "visibiity": {
                            "type": "string",
                            "enum": ["public", "private"]
                        },
                        "options": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "string"
                            }
                        },
                        "regions": _regions,
                        "vcpus": {
                            "type": "string",
                            "pattern": "^[0-9]+$"
                        },
                        "swap": {
                            "type": "string",
                            "pattern": "^[0-9]+$"
                        },
                        "disk": {
                            "type": "string",
                            "pattern": "^[0-9]+$"
                        },
                        "tenants": _tenants,
                        "id": {"type": "string"},
                        "name": {"type": "string"}
                    },
                    "required": ["status", "description", "series",
                                 "extra-specs", "ram", "ephemeral",
                                 "visibility", "vcpus", "regions", "swap",
                                 "disk", "tenants", "id", "name"]
                }
            }
        },
        "required": ["flavors"]
    }
}

get_extra_specs = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'os_extra_specs': _extra_specs
        }
    }
}

add_extra_specs = {
    "status_code": [201],
    'response_body': {
        'type': 'object',
        'properties': {
            'os_extra_specs': _extra_specs
        }
    }
}

update_extra_specs = get_extra_specs

delete_extra_specs = {
    "status_code": [204]
}

add_tags = {
    'status_code': [201],
    'response_body': _tags
}

delete_tags = {
    "status_code": [204]
}

get_tags = {
    'status_code': [200],
    'response_body': _tags
}

update_tags = get_tags

add_region = {
    'status_code': [201],
    'response_body': {
        'type': 'object',
        'properties': {
            'regions': _regions
        }
    }
}

delete_region = {
    "status_code": [204]
}

add_tenant = {
    'status_code': [201],
    'response_body': {
        'type': 'object',
        'properties': {
            'tenants': _tenants
        }
    }
}

delete_tenant = {
    "status_code": [204]
}
