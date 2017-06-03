"""unittest get resource."""
from mock import patch

import rds.controllers.v1.resources.root as root
from rds.tests.controllers.v1.functional_test import FunctionalTest


class TestCreateResource(FunctionalTest):
    """tests for only for api handler."""

    @patch.object(root.ResourceService, 'main', return_value="12345")
    def test_create_resource_success(self, input):
        """test create resource as it succeed."""
        response = self.app.post_json('/v1/rds/resources', good_data)
        assert response.json['customer']['id'] == '12345'
        assert response.status_int == 201

    @patch.object(root.ResourceService, 'main', return_value="12345")
    def test_create_resource_success_flavor(self, input):
        """test create flavor as it succeed."""
        response = self.app.post_json('/v1/rds/resources', flavor_data)
        assert response.json['flavor']['id'] == '12345'
        assert response.status_int == 201

    @patch.object(root.ResourceService, 'main', return_value="12345")
    def test_create_resource_success_image(self, input):
        """test create flavor as it succeed."""
        response = self.app.post_json('/v1/rds/resources', image_data)
        assert response.json['image']['id'] == '12345'
        assert response.status_int == 201

    @patch.object(root.ResourceService, 'main',
                  side_effect=Exception("general exception"))
    def test_create_resource_gen_except(self, input):
        """test creatte resource to catch general exception."""
        response = self.app.post_json('/v1/rds/resources',
                                      good_data, expect_errors=True)
        assert response.status_int == 400

    @patch.object(root.ResourceService, 'main',
                  side_effect=root.ConflictValue("region"))
    def test_create_resource_conflict_except(self, input):
        """test creatte resource to catch ConflictValue exception."""
        response = self.app.post_json('/v1/rds/resources',
                                      good_data, expect_errors=True)
        assert response.status_int == 409

    @patch.object(root.ResourceService, 'main', return_value="12345")
    def test_delete_resource_flavor(self, input):
        """test delete flavor."""
        response = self.app.delete_json('/v1/rds/resources', flavor_data)
        assert response.status_int == 200

    @patch.object(root.ResourceService, 'main', return_value="12345")
    def test_delete_resource_any(self, input):
        """test delete resource not flavor."""
        flavor_data["service_template"]["resource"]['resource_type'] = \
            "customer"
        response = self.app.delete_json('/v1/rds/resources', flavor_data,
                                        expect_errors=True)
        assert response.status_int == 405
        flavor_data["service_template"]["resource"]['resource_type'] = "flavor"

    @patch.object(root.ResourceService, 'main',
                  side_effect=root.ConflictValue("region"))
    def test_delete_resource_flavor_con(self, input):
        """test delete flavor while previous proccess still in progress."""
        try:
            response = self.app.delete_json('/v1/rds/resources', flavor_data)
        except Exception as e:
            if '409 Conflict' not in str(e.message):
                self.fail('error')

    @patch.object(root.ResourceService, 'main',
                  side_effect=Exception("unknown error"))
    def test_delete_resource_flavor_exce(self, input):
        """test delete flavor with general; exception."""
        try:
            response = self.app.delete_json('/v1/rds/resources', flavor_data)
        except Exception as e:
            if 'unknown error' not in str(e.message):
                self.fail('error')

    @patch.object(root.ResourceService, 'main', return_value="12345")
    def test_update_resource_success(self, input):
        updated =False
        """test update resource as it succeed."""
        response = self.app.put_json('/v1/rds/resources', good_data)
        if 'updated' in response.json['customer']:
            updated = True
        assert response.json['customer']['id'] == '12345'
        assert response.status_int == 201
        assert updated == True

    @patch.object(root.ResourceService, 'main',
                  side_effect=Exception("unknown error"))
    def test_put_resource_gen_exce(self, input):
        """test customer put with general; exception."""
        try:
            response = self.app.put_json('/v1/rds/resources', good_data)
        except Exception as e:
            if 'unknown error' not in str(e.message):
                self.fail('error')

    @patch.object(root.ResourceService, 'main',
                  side_effect=root.ConflictValue("region"))
    def test_modify_resource_conflict_except(self, input):
        """test modify resource to catch ConflictValue exception."""
        response = self.app.put_json('/v1/rds/resources',
                                      good_data, expect_errors=True)
        assert response.status_int == 409

good_data = {
    "service_template": {
        "resource": {
            "resource_type": "customer"
            },
        "model": "{\n  \"uuid\": \"1e24981a-fa51-11e5-86aa-5e5517507c6"
                 "6\",\n  \"description\": \"this is a description\",\n  \"nam"
                 "e\": \"testname\",\n  \"enabled\": 1,\n  \"default_regio"
                 "n\": {\n      \"name\": \"regionnamezzzz\",\n      \"quota"
                 "s\":[\n          {\n            \"compute\": \n             "
                 " {\n                \"instances\": \"10\",\n                "
                 "\"injected_files\": \"10\",\n                \"keypair"
                 "s\": \"10\",\n                \"ram\": \"10\"\n           "
                 "   },\n            \"storage\":\n              {\n        "
                 "        \"gigabytes\": \"10\",\n                \"snapsho"
                 "ts\": \"10\",\n                \"volumes\": \"10\"\n      "
                 "        },\n            \"network\": \n              {\n  "
                 "              \"floatingip\": \"10\",\n                \"ne"
                 "twork\": \"10\",\n                \"port\": \"10\",\n      "
                 "          \"router\": \"10\",\n                \"subnet\":"
                 " \"10\"\n              }\n            }\n        ],\n      "
                 "\"users\": [\n        {\n          \"id\": \"userId1zzz"
                 "z\",\n          \"roles\": [\n              \"admi"
                 "nzzzz\",\n\t\t\t  \"otherzzzzz\"\n          ]\n        "
                 "},\n\t\t{\n          \"id\": \"userId2zzz\",\n          \"ro"
                 "les\": [\n\t\t\t  \"storagezzzzz\"\n          ]\n        "
                 "}\n      ]\n    },\n  \"regions\": [\n    {\n      \"nam"
                 "e\": \"regionname\",\n      \"quotas\":[\n          {\n     "
                 "       \"compute\": \n              {\n                \"ins"
                 "tances\": \"10\",\n                \"injected_file"
                 "s\": \"10\",\n                \"keypairs\": \"10\",\n       "
                 "         \"ram\": \"10\"\n              },\n            \"st"
                 "orage\":\n              {\n                \"gigabyte"
                 "s\": \"10\",\n                \"snapshots\": \"10\",\n     "
                 "           \"volumes\": \"10\"\n              },\n         "
                 "   \"network\": \n              {\n                \"floati"
                 "ngip\": \"10\",\n                \"network\": \"10\",\n    "
                 "            \"port\": \"10\",\n                \"route"
                 "r\": \"10\",\n                \"subnet\": \"10\"\n         "
                 "     }\n            }\n        ],\n      \"users\": [\n    "
                 "    {\n          \"id\": \"userId1\",\n          \"role"
                 "s\": [\n              \"admin\",\n\t\t\t  \"other\"\n      "
                 "    ]\n        },\n\t\t{\n          \"id\": \"userId2\",\n "
                 "         \"roles\": [\n\t\t\t  \"storage\"\n          ]\n  "
                 "      }\n      ]\n    },\n\t{\n      \"name\": \"regionname"
                 "test\",\n      \"quotas\":[\n          {\n            \"com"
                 "pute\": \n              {\n                \"instanc"
                 "es\": \"10\",\n                \"injected_files\": \"10\",\n"
                 "                \"keypairs\": \"10\",\n                \"ra"
                 "m\": \"10\"\n              },\n            \"storage\":\n  "
                 "            {\n                \"gigabytes\": \"10\",\n    "
                 "            \"snapshots\": \"10\",\n                \"volum"
                 "es\": \"10\"\n              },\n            \"network\": \n"
                 "              {\n                \"floatingip\": \"10\",\n "
                 "               \"network\": \"10\",\n                \"por"
                 "t\": \"10\",\n                \"router\": \"10\",\n        "
                 "        \"subnet\": \"10\"\n              }\n            "
                 "}\n        ],\n      \"users\": [\n        {\n          \"i"
                 "d\": \"userId1test\",\n          \"roles\": [\n           "
                 "   \"admintest\",\n\t\t\t  \"othertest\"\n          ]\n   "
                 "     },\n\t\t{\n          \"id\": \"userId2test\",\n      "
                 "    \"roles\": [\n\t\t\t  \"storagetest\"\n          ]\n  "
                 "      }\n      ]\n    }\n  ]\n}",
        "tracking": {
            "external_id": "SSP-session1234",
            "tracking_id": "uuid-12345"
            }
        }
    }

flavor_data = {
    "service_template": {
        "resource": {
            "resource_type": "flavor"
            },
        "model": "{\n            \"status\": \"complete\",\n            \"pr"
                 "ofile\": \"P2\",\n            \"regions\": [\n            "
                 "    {\n                    \"name\": \"0\"\n              "
                 "  },\n                {\n                    \"nam"
                 "e\": \"1\"\n                }\n            ],\n            "
                 "\"description\": \"First flavor for AMAR\",\n            \"r"
                 "am\": 64,\n            \"visibility\": \"public\",\n       "
                 "     \"extra_specs\": {\n                \"key1\": \"value"
                 "1\",\n                \"key2\": \"value2\",\n              "
                 "  \"keyx\": \"valuex\"\n            },\n            \"vcpu"
                 "s\": 2,\n            \"swap\": 51231,\n            \"tenan"
                 "ts\": [\n                {\n                    \"tenant_"
                 "id\": \"abcd-efgh-ijkl-4567\"\n                },\n       "
                 "         {\n                    \"tenant_id\": \"abcd-efgh-"
                 "ijkl-4567\"\n                }\n            ],\n            "
                 "\"disk\": 512,\n            \"empheral\": 1,\n            "
                 "\"id\": \"uuid-uuid-uuid-uuid\",\n            \"name\": \"N"
                 "ice Flavor\"\n        }",
        "tracking": {
            "external_id": "SSP-session1234",
            "tracking_id": "uuid-12345"
            }
        }
    }

image_data = {
    "service_template": {
        "resource": {
            "resource_type": "image"
        },
        "model": "{  \r\n   \"internal_id\":1,\r\n   \"id\":\"uuu1id12-uuid-uuid-uuid\",\r\n  "
                 " \"name\":\"Ubuntu\",\r\n   \"enabled\": 1,\r\n   \"protected\": 1,\r\n  "
                 " \"url\": \"https:\/\/mirrors.it.att.com\/images\/image-name\",\r\n "
                 "  \"visibility\": \"public\",\r\n   \"disk_format\": \"raw\",\r\n  "
                 " \"container_format\": \"bare\",\r\n   \"min_disk\":2,\r\n   \"min_ram\":0,\r\n "
                 "  \"regions\":[  \r\n      {  \r\n         \"name\":\"North\",\r\n        "
                 " \"type\":\"single\",\r\n         \"action\": \"delete\",\r\n         "
                 "\"image_internal_id\":1\r\n      },\r\n      {  \r\n         \"name\":\"North\",\r\n        "
                 " \"action\": \"create\",\r\n         \"type\":\"single\",\r\n        "
                 " \"image_internal_id\":1\r\n      }\r\n   ],\r\n   \"image_properties\":[  \r\n      {  \r\n        "
                 " \"key_name\":\"Key1\",\r\n         \"key_value\":\"Key1.value\",\r\n         "
                 "\"image_internal_id\":1\r\n      },\r\n      {  \r\n         \"key_name\":\"Key2\",\r\n  "
                 "       \"key_value\":\"Key2.value\",\r\n         \"image_internal_id\":1\r\n    "
                 "  }\r\n   ],\r\n   \"image_tenant\":[  \r\n      {  \r\n         \"tenant_id\":\"abcd-efgh-ijkl-4567\",\r\n  "
                 "       \"image_internal_id\":1\r\n      },\r\n      {  \r\n       "
                 "  \"tenant_id\":\"abcd-efgh-ijkl-4567\",\r\n         \"image_internal_id\":1\r\n      }\r\n   ],\r\n "
                 "  \"image_tags\":[  \r\n      {  \r\n         \"tag\":\"abcd-efgh-ijkl-4567\",\r\n     "
                 "    \"image_internal_id\":1\r\n      },\r\n      {  \r\n         \"tag\":\"abcd-efgh-ijkl-4567\",\r\n   "
                 "      \"image_internal_id\":1\r\n      }\r\n   ],\r\n   \"status\":\"complete\",\r\n}",
        "tracking": {
            "external_id": "SSP-session1234",
            "tracking_id": "uuid-12345"
        }
    }
}
