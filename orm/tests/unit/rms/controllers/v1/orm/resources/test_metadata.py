import json

from mock import patch, MagicMock

from orm.services.region_manager.rms.controllers.v2.orm.resources import metadata
from orm.services.region_manager.rms.model.model import *
from orm.tests.unit.rms import FunctionalTest

from wsme.exc import ClientSideError

result_inst = RegionData("1", "2", "3", "4", "5", "6",
                         endpoints=[
                             EndPoint("http://www.example.co.il", "url")
                         ],
                         address=Address("US", "NY", "HANEGEV", "AIRPORT_CITY", "5"),
                         metadata={"key1": ["value1"], "key2": ["value2"]})

result_dict = {u'status': u'2', u'vlcpName': None, u'clli': u'5',
               u'name': u'4', u'designType': None,
               u'AicVersion': u'6', u'OSVersion': None, u'id': u'3',
               u'address': {u'country': u'US', u'state': u'NY',
                            u'street': u'AIRPORT_CITY',
                            u'zip': u'5', u'city': u'HANEGEV'},
               u'endpoints': [
                   {u'type': u'url',
                    u'publicURL': u'http://www.example.co.il'}],
               u'locationType': None,
               u'metadata': {u'key1': [u'value1'],
                             u'key2': [u'value2']}
               }

metadata_input_dict = {
    "metadata": {
        "key1": ["value1"],
        "key2": ["value2"]
    }
}


metadata_result_dict = {u'metadata': {u'key1': [u'value1'],
                                      u'key2': [u'value2']
                                      }
                        }

metadata_result_empty_dict = {u'metadata': {}}


class TestMetadataController(FunctionalTest):

    ###############
    # Test DELETE api
#    @patch.object(metadata, 'request')
#    @patch.object(metadata, 'authentication')
#    @patch.object(metadata.RegionService, 'delete_metadata_from_region')
#    def test_delete_success(self, result, mock_auth, mock_request):
#        response = self.app.delete('/v2/orm/regions/my_region/metadata/mykey',
#                                   expect_errors=True)
#        self.assertEqual(response.status_int, 204)

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'delete_metadata_from_region',
                  side_effect=metadata.error_base.NotFoundError("region not found !!!?"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 404,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '774',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=404))
    def test_delete_with_region_not_exist(self, get_err, result,
                                          mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.delete('/v2/orm/regions/my_region/metadata/key',
                                   expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('774', result_json['transaction_id'])
        self.assertEqual(404, result_json['code'])

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'delete_metadata_from_region',
                  side_effect=Exception("unknown error"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '771',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    # @patch.object(metadata, 'authentication')
    def test_delete_region_metadata_unknown_exception(self, err, result,
                                                      mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.delete('/v2/orm/regions/my_region/metadata/key',
                                   expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('771', result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])

    ###############
    # Test PUT api
    # @patch.object(metadata, 'request')
    # @patch.object(metadata, 'authentication')
    # @patch.object(metadata.RegionService, 'update_region_metadata',
    #               return_value=result_inst.metadata)
    # def test_put_success(self, result, mock_auth, mock_request):
    #     response = self.app.put_json('/v2/orm/regions/my_region/metadata',
    #                                  metadata_input_dict)
    #     self.assertEqual(dict(response.json), metadata_result_dict)

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'update_region_metadata',
                  side_effect=metadata.error_base.NotFoundError("region not found !!!?"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 404,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '888',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=404))
    def test_put_update_region_metadata_with_region_not_exist(self, get_err,
                                                              result,
                                                              mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.put_json('/v2/orm/regions/my_region/metadata',
                                     metadata_input_dict, expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('888', result_json['transaction_id'])
        self.assertEqual(404, result_json['code'])

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'update_region_metadata',
                  side_effect=Exception("unknown error"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '777',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    # @patch.object(metadata, 'authentication')
    def test_put_update_region_metadata_unknown_exception(self, err, result,
                                                          mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.put_json('/v2/orm/regions/my_region/metadata',
                                     metadata_input_dict, expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('777', result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])

    ###############
    # Test POST api
    # @patch.object(metadata, 'request')
    # @patch.object(metadata, 'authentication')
    # @patch.object(metadata.RegionService, 'add_region_metadata',
    #               return_value=result_inst.metadata)
    # def test_post_success(self, result, mock_auth, mock_request):
    #     response = self.app.post_json('/v2/orm/regions/my_region/metadata',
    #                                   metadata_input_dict)
    #     self.assertEqual(dict(response.json), metadata_result_dict)

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'add_region_metadata',
                  side_effect=metadata.error_base.NotFoundError("region not found !!!?"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 404,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '333',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=404))
    def test_post_add_region_metadata_with_region_not_exist(self, get_err,
                                                            result, mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.post_json('/v2/orm/regions/my_region/metadata',
                                      metadata_input_dict, expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('333', result_json['transaction_id'])
        self.assertEqual(404, result_json['code'])

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'add_region_metadata',
                  side_effect=metadata.error_base.ConflictError("unknown error"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 409,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '999',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=409))
    # @patch.object(metadata, 'authentication')
    def test_post_add_region_metadata_with_duplicate(self, err, result,
                                                     mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.post_json('/v2/orm/regions/my_region/metadata',
                                      metadata_input_dict, expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('999', result_json['transaction_id'])
        self.assertEqual(409, result_json['code'])

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'add_region_metadata',
                  side_effect=Exception("unknown error"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '444',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    # @patch.object(metadata, 'authentication')
    def test_post_add_region_metadata_unknown_exception(self, err, result,
                                                        mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.post_json('/v2/orm/regions/my_region/metadata',
                                      metadata_input_dict, expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('444', result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])

    ##############
    # Test GET api
    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'get_region_by_id_or_name',
                  return_value=result_inst)
    def test_get_success(self, result, mock_auth):
        response = self.app.get('/v2/orm/regions/my_region/metadata')
        self.assertEqual(dict(response.json), metadata_result_dict)

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'get_region_by_id_or_name',
                  side_effect=Exception("unknown error"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '111',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    # @patch.object(metadata, 'authentication')
    def test_get_get_region_by_id_or_name_throws_exception(self, err, result,
                                                           mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.get('/v2/orm/regions/my_region/metadata', expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('111', result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])

    @patch.object(metadata, 'authentication')
    @patch.object(metadata.RegionService, 'get_region_by_id_or_name',
                  side_effect=metadata.error_base.NotFoundError("no content !!!?"))
    @patch.object(metadata.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 404,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '222',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=404))
    def test_get_get_region_by_id_or_name_region_not_found(self, get_err,
                                                           result, mock_auth):
        temp_request = metadata.request
        metadata.request = MagicMock()

        response = self.app.get('/v2/orm/regions/my_region/metadata', expect_errors=True)

        metadata.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('222', result_json['transaction_id'])
        self.assertEqual(404, result_json['code'])
