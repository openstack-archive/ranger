import time
from unittest import TestCase

import mock
from orm_common.utils import cross_api_utils


class TestCrossApiUtil(TestCase):
    @mock.patch('pecan.conf')
    def setUp(self, mock_conf):
        self.mock_response = mock.Mock()
        cross_api_utils.conf = mock_conf

    def respond(self, value, code):
        self.mock_response.json.return_value = value
        self.mock_response.status_code = code
        return self.mock_response

    def test_set_utils_conf(self):
        cross_api_utils.set_utils_conf(None)
        self.assertEqual(cross_api_utils.conf, None)

    def test_check_conf_initialization(self):
        cross_api_utils.set_utils_conf(None)
        self.assertRaises(AssertionError, cross_api_utils._check_conf_initialization)

    @mock.patch('orm_common.utils.cross_api_utils.get_rms_region_group')
    def test_is_region_group_exist(self, mock_rms_region_group):
        mock_rms_region_group.return_value = 'test_group'
        exist = cross_api_utils.is_region_group_exist('test_group_name')
        self.assertEqual(exist, True)

    @mock.patch('orm_common.utils.cross_api_utils.get_rms_region_group')
    def test_is_region_group_exist_false(self, mock_rms_region_group):
        mock_rms_region_group.return_value = None
        exist = cross_api_utils.is_region_group_exist('test_group_name')
        self.assertEqual(exist, False)

    @mock.patch('orm_common.utils.cross_api_utils.get_rms_region_group')
    def test_get_regions_of_group(self, mock_rms_region_group):
        mock_rms_region_group.return_value = {'regions': 'group'}
        exist = cross_api_utils.get_regions_of_group('test_group_name')
        self.assertEqual(exist, 'group')

    @mock.patch('orm_common.utils.cross_api_utils.get_rms_region_group')
    def test_get_regions_of_group_false(self, mock_rms_region_group):
        mock_rms_region_group.return_value = None
        exist = cross_api_utils.get_regions_of_group('test_group_name')
        self.assertEqual(exist, None)

    @mock.patch('requests.get')
    def test_get_rms_region_group(self, mock_get):
        mock_get.return_value = self.respond({'result': 'success'}, 200)
        result = cross_api_utils.get_rms_region_group('test_group_name')
        self.assertEqual(result, {'result': 'success'})

    def test_get_rms_region_group_cache_used(self):
        cross_api_utils.prev_timestamp = time.time()
        cross_api_utils.prev_group_name = 'test_group'
        cross_api_utils.prev_resp = 'test_response'
        cross_api_utils.conf.api.rms_server.cache_seconds = 14760251830
        self.assertEqual(cross_api_utils.prev_resp,
                         cross_api_utils.get_rms_region_group(
                             cross_api_utils.prev_group_name))

    @mock.patch.object(cross_api_utils, 'logger')
    @mock.patch.object(time, 'time', side_effect=ValueError('test'))
    def test_get_rms_region_group_cache_used(self, mock_time, mock_logger):
        self.assertRaises(ValueError, cross_api_utils.get_rms_region_group,
                          'test')

    # @mock.patch('requests.get')
    # def test_get_rms_region_group_with_exception(self, mock_get):
    #    mock_get.side_affect = Exception('boom')
    #    self.assertRaises(Exception, cross_api_utils.get_rms_region_group, 'test_group_name')
