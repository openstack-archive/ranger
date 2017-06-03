from mock import patch, MagicMock
from wsme.exc import ClientSideError

from rms.services import services
from rms.controllers import lcp_controller

from rms.model.model import RegionData, Regions, EndPoint
from rms.services.error_base import NotFoundError

import json

from rms.controllers import lcp_controller as lcps

from rms.tests import FunctionalTest


TEST_REGIONS_DATA = [
    {
        "status": "1",
        "vLCP_name": "n/a",
        "ORD_EP": "http://ord1.com",
        "horizon_EP": "http://horizon1.com",
        "design_type": "n/a",
        "AIC_version": "ranger_agent1.0",
        "id": "SNA1",
        "OS_version": "kilo",
        "keystone_EP": "http://identity1.com",
        "zone_name": "SNA1",
        "location_type": "n/a"
    },
    {
        "status": "0",
        "vLCP_name": "n/a",
        "ORD_EP": "http://ord2.com",
        "horizon_EP": "http://horizon2.com",
        "design_type": "n/a",
        "AIC_version": "ranger_agent1.5",
        "id": "SNA2",
        "OS_version": "kilo",
        "keystone_EP": "http://identity2.com",
        "zone_name": "SNA2",
        "location_type": "n/a"
    },
]

end_point_ord_1 = EndPoint(publicurl="http://ord1.com",
                           type="ord")
end_point_identity_1 = EndPoint(publicurl="http://identity1.com",
                                type="identity")
end_point_horizon_1 = EndPoint(publicurl="http://horizon1.com",
                               type="dashboard")

end_point_ord_2 = EndPoint(publicurl="http://ord2.com",
                           type="ord")
end_point_identity_2 = EndPoint(publicurl="http://identity2.com",
                                type="identity")
end_point_horizon_2 = EndPoint(publicurl="http://horizon2.com",
                               type="dashboard")
end_points_1 = [end_point_ord_1, end_point_identity_1, end_point_horizon_1]
end_points_2 = [end_point_ord_2, end_point_identity_2, end_point_horizon_2]

region_data_sna1 = RegionData(status="functional", id="SNA1", name="SNA 1",
                              clli="n/a", ranger_agent_version="ranger_agent1.0", design_type="n/a",
                              location_type="n/a", vlcp_name="n/a", open_stack_version="kilo",
                              endpoints=end_points_1)
region_data_sna2 = RegionData(status="down", id="SNA2", name="SNA 2",
                              clli="n/a", ranger_agent_version="ranger_agent1.5", design_type="n/a",
                              location_type="n/a", vlcp_name="n/a", open_stack_version="kilo",
                              endpoints=end_points_2)
region_data_no_endpoints = RegionData(status="functional", id="SNA2", name="SNA 2",
                                      clli="n/a", ranger_agent_version="ranger_agent1.5", design_type="n/a",
                                      location_type="n/a", vlcp_name="n/a", open_stack_version="kilo")

regions_mock = Regions([region_data_sna1, region_data_sna2])


class TestLcpController(FunctionalTest):

    @patch.object(services, 'get_regions_data', return_value=regions_mock)
    def test_get_zones_success(self, regions_data):
        zones = lcps.get_zones()
        self.assertEqual(zones, TEST_REGIONS_DATA)

    @patch.object(services, 'get_regions_data',
                  side_effect=NotFoundError(message="No regions found!"))
    def test_get_zones_get_regions_data_error(self, regions_data):
        zones = lcps.get_zones()
        self.assertEqual(zones, [])

    # Test get_all in lcp_controller
    @patch.object(lcp_controller, 'get_zones', return_value=TEST_REGIONS_DATA)
    @patch.object(lcp_controller, 'authentication')
    def test_get_all_success(self, mock_authentication, get_zones):

        response = self.app.get('/lcp', expect_errors=True)
        response_json = json.loads(response.body)

        self.assertEqual(response_json, TEST_REGIONS_DATA)
        self.assertEqual(response.status_int, 200)

    @patch.object(lcp_controller, 'get_zones',
                  side_effect=Exception("unknown error"))
    @patch.object(lcp_controller.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '999',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    @patch.object(lcp_controller, 'authentication')
    def test_get_all_get_zones_error(self, mock_auth, err, get_zones):
        temp_request = lcp_controller.request
        lcp_controller.request = MagicMock()

        response = self.app.get('/lcp', expect_errors=True)

        lcp_controller.request = temp_request

        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual("999", result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])

    # Test get_one in lcp_controller
    @patch.object(lcp_controller, 'get_zones', return_value=TEST_REGIONS_DATA)
    @patch.object(lcp_controller, 'authentication')
    def test_get_one_success(self, mock_authentication, get_zones):

        response = self.app.get('/lcp/SNA1/', expect_errors=True)
        response_json = json.loads(response.body)

        self.assertEqual(response_json["zone_name"], "SNA1")
        self.assertEqual(response_json["id"], "SNA1")
        self.assertEqual(response.status_int, 200)

    @patch.object(lcp_controller, 'get_zones',
                  side_effect=Exception("unknown error"))
    @patch.object(lcp_controller.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 500,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '555',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=500))
    @patch.object(lcp_controller, 'authentication')
    def test_get_one_get_zones_error(self, mock_auth, err, get_zones):
        temp_request = lcp_controller.request
        lcp_controller.request = MagicMock()

        response = self.app.get('/lcp/1234', expect_errors=True)

        lcp_controller.request = temp_request

        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual("555", result_json['transaction_id'])
        self.assertEqual(500, result_json['code'])

    @patch.object(lcp_controller, 'get_zones', return_value=[])
    @patch.object(lcp_controller.err_utils, 'get_error',
                  return_value=ClientSideError(json.dumps({
                      'code': 404,
                      'type': 'test',
                      'created': '0.0',
                      'transaction_id': '444',
                      'message': 'test',
                      'details': 'test'
                  }), status_code=404))
    @patch.object(lcp_controller, 'authentication')
    def test_get_one_not_found(self, mock_auth, err, get_zones):
        temp_request = lcp_controller.request
        lcp_controller.request = MagicMock()

        response = self.app.get('/lcp/1234', expect_errors=True)

        lcp_controller.request = temp_request

        dict_body = json.loads(response.body)
        result_json = json.loads(dict_body['faultstring'])

        self.assertEqual("444", result_json['transaction_id'])
        self.assertEqual(404, result_json['code'])

    # Test get_one in lcp_controller
    def test_build_zone_response_with_missing_endpoints(self,):
        result = lcps.build_zone_response(region_data_no_endpoints)
        self.assertEqual("", result['keystone_EP'])
        self.assertEqual("", result['horizon_EP'])
        self.assertEqual("", result['ORD_EP'])
