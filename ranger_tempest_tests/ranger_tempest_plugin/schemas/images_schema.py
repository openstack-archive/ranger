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

_region_status = {
    "type": "string",
    "enum": ["Submitted", "Pending", "Success", "Error"]
}

_regions = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "status": _region_status,
            "name": {"type": "string"},
            "checksum": {"type": "string"},
            "size": {"type": "string"},
            "virtual_size": {"type": "string"},
            "type": {"type": "string"},
            "error_message": {"type": "string"}
        }
    }
}

_tags = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

_status = {
    "type": "string",
    "enum": ["Success", "no regions", "Error", "Pending"]
}

_links = {
    "type": "object",
    "properties": {
        "self": {"type": "string"}
    },
    "required": ["self"]
}

_image = {
    "type": "object",
    "properties": {
        "image": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "links": {
                    "type": "object",
                    "items": {
                        "self": {"type": "string"}
                    }
                },
                "locations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "file": {"type": "string"},
                "owner": {"type": "string"},
                "id": {"type": "string"},
                "self": {"type": "string"},
                "created-at": {"type": "string"},
                "updated-at": {"type": "string"},
                "regions": _regions,
                "disk-format": {"type": "string"},
                "min-ram": {
                    "type": "number"
                },
                "schema": {"type": "string"},
                "status": _status,
                "customers": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "tags": _tags,
                "visibility": {
                    "type": "string",
                    "enum": ["public", "private"]
                },
                "min-disk": {
                    "type": "number"
                },
                "properties": {
                    "type": "object",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "name": {"type": "string"},
                "url": {"type": "string"},
                "protected": {
                    "type": "boolean"
                },
                "container-format": {"type": "string"}
            },
            "required": ["links", "enabled", "locations", "file",
                         "status", "owner", "id", "self", "disk-format",
                         "min-ram", "properties", "visibility",
                         "regions", "schema", "min-disk", "customers",
                         "protected", "url", "name", "container-format"]
        }
    },
    "required": ["image"]
}

create_image = {
    "status_code": [201],
    "response_body": _image
}

add_tenant_to_image = {
    "status_code": [201],
    "response_body": _image
}

get_image = {
    "status_code": [200],
    "response_body": _image
}

update_tenant = get_image

update_image = get_image

delete_image = {
    "status_code": [204]
}

delete_tenant_from_image = {
    "status_code": [204]
}

add_region = {
    "status_code": [200, 201],
    'response_body': {
        'type': 'object',
        'properties': {
            'regions': _regions
        }
    }
}

delete_region = delete_image

_region_names_array = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

list_images = {
    "status_code": [200],
    "response_body": {
        "type": "object",
        "properties": {
            "images": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "status": _status,
                        "regions": _region_names_array,
                        "name": {"type": "string"},
                        "visibiity": {
                            "type": "string",
                            "enum": ["public", "private"]
                        },
                        "id": {"type": "string"}
                    },
                    "required": ["status", "regions", "name",
                                 "visibility", "id"]
                }
            }
        },
        "required": ["images"]
    }
}

enable_image_resp = get_image
