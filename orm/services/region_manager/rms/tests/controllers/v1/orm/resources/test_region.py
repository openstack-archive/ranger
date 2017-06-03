import json
from mock import patch, MagicMock

from rms.controllers.v2.orm.resources import regions
from rms.model import model as PyModels
from rms.tests import FunctionalTest

from wsme.exc import ClientSideError


result_inst = PyModels.Regions([PyModels.RegionData("2", "3", "4", "5", "6",
                                                    address=PyModels.Address("US", "NY", "HANEGEV", "AIRPORT_CITY", "5"),
                                                    endpoints=[
                                                        PyModels.EndPoint("http://www.example.co.il", "url")
                                                    ],
                                                    metadata={"key1": ["value1"], "key2": ["value2"]}),
                                PyModels.RegionData("2", "3", "4", "5", "6", endpoints=[
                                    PyModels.EndPoint("http://www.example.co.il", "url")],
                                address=PyModels.Address("US", "NY", "HANEGEV", "AIRPORT_CITY", "5"),
                                metadata={"key3": ["value3"], "key4": ["value4"]})])


result_dict = {u'regions': [{u'status': u'2', u'vlcpName': None, u'CLLI': u'5',
                             u'name': u'3', u'designType': None,
                             u'rangerAgentVersion': u'6', u'OSVersion': None, u'id': u'3',
                             u'address': {u'country': u'US', u'state': u'NY',
                                          u'street': u'AIRPORT_CITY',
                                          u'zip': u'5', u'city': u'HANEGEV'},
                             u'endpoints': [
                                 {u'type': u'url',
                                  u'publicURL': u'http://www.example.co.il'}],
                             u'locationType': None,
                             u'metadata': {u'key1': [u'value1'],
                                           u'key2': [u'value2']}},
                            {u'status': u'2', u'vlcpName': None, u'CLLI': u'5',
                             u'name': u'3', u'designType': None,
                             u'rangerAgentVersion': u'6', u'OSVersion': None,
                             u'id': u'3',
                             u'address': {u'country': u'US',
                                          u'state': u'NY',
                                          u'street': u'AIRPORT_CITY',
                                          u'zip': u'5', u'city': u'HANEGEV'},
                             u'endpoints': [{u'type': u'url',
                                             u'publicURL': u'http://www.example.co.il'}],
                             u'locationType': None,
                             u'metadata': {u'key3': [u'value3'],
                                           u'key4': [u'value4']}}]}


db_full_region = {
    'region_status': 'functional',
    'address_city': 'LAb',
    'CLLI': 'nn/a',
    'region_id': 'SNA20',
    'open_stack_version': 'kilo',
    'address_country': 'US',
    'design_type': 'n/a',
    'ranger_agent_version': 'ranger_agent1.0',
    'vlcp_name': 'n/a',
    'end_point_list': [{
        'url': 'http://horizon1.com',
        'type': 'dashboard'
    }, {
        'url': 'http://identity1.com',
        'type': 'identity'
    }, {
        'url': 'http://identity1.com',
        'type': 'identity222333'
    }, {
        'url': 'http://ord1.com',
        'type': 'ord'
    }],
    'meta_data_dict': {
        'A': ['b']
    },
    'address_state': 'CAL',
    'address_zip': '1111',
    'address_street': 'n/a',
    'location_type': 'n/a',
    'name': 'SNA 18'
}

full_region = {
    "status": "functional",
    "endpoints":
        [
            {
                "type": "dashboard",
                "publicURL": "http://horizon1.com"
            },

            {
                "type": "identity",
                "publicURL": "http://identity1.com"
            },
            {
                "type": "identity222333",
                "publicURL": "http://identity1.com"
            },
            {
                "type": "ord",
                "publicURL": "http://ord1.com"
            }
        ],
        "CLLI": "nn/a",
        "name": "SNA20",
        "designType": "n/a",
        "locationType": "n/a",
        "vlcpName": "n/a",
        "address":
            {
                "country": "US",
                "state": "CAL",
                "street": "n/a",
                "zip": "1111",
                "city": "LAb"},
        "rangerAgentVersion": "ranger_agent1.0",
        "OSVersion": "kilo",
        "id": "SNA20",
        "metadata":
            {"A": ["b"]}
}


class TestAddRegion(FunctionalTest):

    def get_error(self, transaction_id, status_code, error_details=None, message=None):
        return ClientSideError(json.dumps({
            'code': status_code,
            'type': 'test',
            'created': '0.0',
            'transaction_id': transaction_id,
            'message': message if message else error_details,
            'details': 'test'
        }), status_code=status_code)

    def _create_result_from_input(self, input):
        obj = PyModels.RegionData()
        obj.clli = full_region["CLLI"]
        obj.name = full_region["id"]  # need to be same as id
        obj.design_type = full_region["designType"]
        obj.location_type = full_region["locationType"]
        obj.vlcp_name = full_region["vlcpName"]
        obj.id = full_region["id"]
        obj.address.country = full_region["address"]["country"]
        obj.address.city = full_region["address"]["city"]
        obj.address.state = full_region["address"]["state"]
        obj.address.street = full_region["address"]["street"]
        obj.address.zip = full_region["address"]["zip"]
        obj.ranger_agent_version = full_region["rangerAgentVersion"]
        obj.open_stack_version = full_region["OSVersion"]
        obj.metadata = full_region["metadata"]
        obj.status = full_region["status"]
        obj.endpoints = []
        for endpoint in full_region["endpoints"]:
            obj.endpoints.append(PyModels.EndPoint(type=endpoint["type"],
                                                   publicurl=endpoint[
                                                       "publicURL"]))
        return obj

    @patch.object(regions, 'request')
    @patch.object(regions.RegionService, 'create_full_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_add_region_success(self, mock_auth, mock_create_logic,
                                mock_request):
        self.maxDiff = None
        mock_create_logic.return_value = self._create_result_from_input(
            full_region)
        response = self.app.post_json('/v2/orm/regions', full_region)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, full_region)

    @patch.object(regions.RegionService, 'create_full_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_add_region_any_error(self, mock_auth, mock_create_logic):
        self.maxDiff = None
        mock_create_logic.side_effect = Exception("unknown error")
        response = self.app.post_json('/v2/orm/regions', full_region,
                                      expect_errors=True)
        self.assertEqual(response.status_code, 500)

    @patch.object(regions, 'request')
    @patch.object(regions, 'err_utils')
    @patch.object(regions.RegionService, 'create_full_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_add_region_value_error(self, mock_auth, mock_create_logic,
                                    mock_get_error, request_mock):
        mock_get_error.get_error = self.get_error
        request_mock.transaction_id = "555"
        mock_create_logic.side_effect = regions.error_base.InputValueError(message="value error")
        response = self.app.post_json('/v2/orm/regions', full_region,
                                      expect_errors=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.json['faultstring'])['message'], 'value error')

    @patch.object(regions.RegionService, 'get_region_by_id_or_name')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_get_region_success(self, mock_auth, mock_create_logic):
        self.maxDiff = None
        mock_create_logic.return_value = self._create_result_from_input(
            full_region)
        response = self.app.get('/v2/orm/regions/id')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, full_region)

    @patch.object(regions, 'request')
    @patch.object(regions, 'err_utils')
    @patch.object(regions.RegionService, 'get_region_by_id_or_name')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_get_region_not_found(self, mock_auth, mock_get_logic,
                                  mock_get_error, mock_request):
        mock_get_error.get_error = self.get_error
        mock_request.transaction_id = "555"
        mock_get_logic.side_effect = regions.error_base.NotFoundError(message="not found", status_code=404)
        response = self.app.get('/v2/orm/regions/id', expect_errors=True)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         'not found')
        self.assertEqual(response.status_code, 404)

    @patch.object(regions, 'request')
    @patch.object(regions, 'err_utils')
    @patch.object(regions.RegionService, 'delete_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_delete_region(self, mock_auth, mock_delete_logic,
                           mock_get_error, mock_request):
        mock_get_error.get_error = self.get_error
        mock_request.transaction_id = "555"
        mock_delete_logic.return_value = True
        response = self.app.delete('/v2/orm/regions/id')
        self.assertEqual(response.status_code, 204)

    @patch.object(regions, 'request')
    @patch.object(regions, 'err_utils')
    @patch.object(regions.RegionService, 'delete_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_delete_region_error(self, mock_auth, mock_delete_logic,
                                 mock_get_error, mock_request):
        mock_get_error.get_error = self.get_error
        mock_request.transaction_id = "555"
        mock_delete_logic.side_effect = Exception("unknown error")
        response = self.app.delete('/v2/orm/regions/id', expect_errors=True)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         'unknown error')

    @patch.object(regions, 'request')
    @patch.object(regions.RegionService, 'update_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_update_region_success(self, mock_auth, mock_update_logic,
                                   mock_request):
        mock_update_logic.return_value = self._create_result_from_input(
            full_region)
        response = self.app.put_json('/v2/orm/regions/id', full_region)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, full_region)

    @patch.object(regions, 'request')
    @patch.object(regions, 'err_utils')
    @patch.object(regions.RegionService, 'update_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_update_region_error(self, mock_auth, mock_update_logic,
                                 mock_get_error, mock_request):
        mock_get_error.get_error = self.get_error
        mock_request.transaction_id = "555"
        mock_update_logic.side_effect = Exception("unknown error2")
        response = self.app.put_json('/v2/orm/regions/id', full_region,
                                     expect_errors=True)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         'unknown error2')

    @patch.object(regions, 'request')
    @patch.object(regions, 'err_utils')
    @patch.object(regions.RegionService, 'update_region')
    @patch.object(regions.authentication, 'authorize', return_value=True)
    def test_update_region_not_found_error(self, mock_auth, mock_update_logic,
                                           mock_get_error, mock_request):
        mock_get_error.get_error = self.get_error
        mock_request.transaction_id = "555"
        mock_update_logic.side_effect = regions.error_base.NotFoundError(
            message="not found", status_code=404)
        response = self.app.put_json('/v2/orm/regions/id', full_region,
                                     expect_errors=True)
        self.assertEqual(json.loads(response.json['faultstring'])['message'],
                         'not found')
        self.assertEqual(response.status_code, 404)


class TestWsmeModelFunctions(TestAddRegion):

    def _to_wsme_from_input(self, input):
        obj = regions.RegionsData()
        obj.clli = full_region["CLLI"]
        obj.name = full_region["name"]
        obj.design_type = full_region["designType"]
        obj.location_type = full_region["locationType"]
        obj.vlcp_name = full_region["vlcpName"]
        obj.id = full_region["id"]
        obj.address.country = full_region["address"]["country"]
        obj.address.city = full_region["address"]["city"]
        obj.address.state = full_region["address"]["state"]
        obj.address.street = full_region["address"]["street"]
        obj.address.zip = full_region["address"]["zip"]
        obj.ranger_agent_version = full_region["rangerAgentVersion"]
        obj.open_stack_version = full_region["OSVersion"]
        obj.metadata = full_region["metadata"]
        obj.status = full_region["status"]
        obj.endpoints = []
        for endpoint in full_region["endpoints"]:
            obj.endpoints.append(regions.EndPoint(type=endpoint["type"],
                                                  publicurl=endpoint[
                                                  "publicURL"]))
        return obj

    def test_region_data_model(self):
        self.maxDiff = None
        wsme_to_python = self._to_wsme_from_input(full_region)._to_clean_python_obj()
        python_obj_input = self._create_result_from_input(full_region)
        self.assertEqual(wsme_to_python.__dict__.pop('address').__dict__,
                         python_obj_input.__dict__.pop('address').__dict__)
        self.assertEqual(wsme_to_python.__dict__.pop('endpoints')[0].__dict__,
                         python_obj_input.__dict__.pop('endpoints')[0].__dict__)
        self.assertEqual(wsme_to_python.__dict__, python_obj_input.__dict__)


class TestGetRegionsController(FunctionalTest):

    @patch.object(regions.RegionService, 'get_regions_data', return_value=result_inst)
    @patch.object(regions, 'authentication')
    def test_get_success(self, mock_authentication, result):
        self.maxDiff = None
        response = self.app.get('/v2/orm/regions')
        self.assertEqual(dict(response.json), result_dict)

    @patch.object(regions.RegionService, 'get_regions_data', side_effect=Exception("unknown error"))
    @patch.object(regions.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '111',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    @patch.object(regions, 'authentication')
    def test_get_unknown_error(self, mock_auth, get_err, result):
        temp_request = regions.request
        regions.request = MagicMock()

        response = self.app.get('/v2/orm/regions', expect_errors=True)

        regions.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('111', result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])

    @patch.object(regions.RegionService, 'get_regions_data',
                  side_effect=regions.error_base.NotFoundError("no content !!!?"))
    @patch.object(regions.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 404,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '222',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=404))
    @patch.object(regions, 'authentication')
    def test_get_region_not_found(self, mock_auth, get_err, result):
        temp_request = regions.request
        regions.request = MagicMock()

        response = self.app.get('/v2/orm/regions', expect_errors=True)

        regions.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('222', result_json['transaction_id'])
        self.assertEqual(404, result_json['code'])

    @patch.object(regions.RegionService, 'get_region_by_id_or_name',
                  return_value=result_inst.regions[0])
    @patch.object(regions, 'authentication')
    def test_get_one_success(self, mock_authentication, result):
        response = self.app.get('/v2/orm/regions/id')
        self.assertEqual(dict(response.json), result_dict['regions'][0])

    @patch.object(regions.RegionService, 'get_regions_data',
                  side_effect=Exception("unknown error"))
    @patch.object(regions.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '111',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    @patch.object(regions, 'authentication')
    def test_get_one_unknown_error(self, mock_auth, get_err, result):
        temp_request = regions.request
        regions.request = MagicMock()

        response = self.app.get('/v2/orm/regions/id', expect_errors=True)

        regions.request = temp_request
        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual('111', result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])
