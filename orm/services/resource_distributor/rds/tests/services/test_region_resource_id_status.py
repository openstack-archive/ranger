import unittest

import mock
from rds.services import region_resource_id_status
from rds.tests import config as conf


class MyResult(object):
    def __init__(self, resource_type, status, timestamp):
        self.resource_type = resource_type
        self.status = status
        self.timestamp = timestamp


class MockClass(object):
    def __init__(self, regions):
        self.regions = regions
        self.done = False

    def __call__(self, *args, **kwargs):
        return self

    def get_records_by_filter_args(self, **kw):
        return self

    def add_update_status_record(self, *args):
        self.done = True


class TestModel(unittest.TestCase):
    def setUp(self):
        region_resource_id_status.config = conf.region_resource_id_status

        self.temp_connection = region_resource_id_status.factory.get_region_resource_id_status_connection

        # Save the original config
        self.temp_config = region_resource_id_status.config

    def tearDown(self):
        # Restore the original config
        region_resource_id_status.config = self.temp_config

        region_resource_id_status.factory.get_region_resource_id_status_connection = self.temp_connection

    def test_validate_status_value_sanity(self):
        test_status = 'test'
        region_resource_id_status.config['allowed_status_values'].add(test_status)
        # Make sure that no exception is raised
        region_resource_id_status.validate_status_value(test_status)

    def test_validate_status_value_invalid_status(self):
        test_status = 'test'
        if test_status in region_resource_id_status.config['allowed_status_values']:
            region_resource_id_status.config['allowed_status_values'].remove(test_status)

        self.assertRaises(region_resource_id_status.InputError,
                          region_resource_id_status.validate_status_value,
                          test_status)

    def test_validate_operation_type_sanity(self):
        test_operation = 'test'
        region_resource_id_status.config['allowed_operation_type'] = {test_operation: 'A'}
        # Make sure that no exception is raised
        region_resource_id_status.validate_operation_type(test_operation)

    def test_validate_operation_type_invalid_operation(self):
        test_operation = 'test'
        region_resource_id_status.config['allowed_operation_type'] = {}

        self.assertRaises(region_resource_id_status.InputError,
                          region_resource_id_status.validate_operation_type,
                          test_operation)

    def test_validate_resource_type_sanity(self):
        test_resource = 'test'
        region_resource_id_status.config['allowed_resource_type'] = {test_resource: 'A'}
        # Make sure that no exception is raised
        region_resource_id_status.validate_resource_type(test_resource)

    def test_validate_resource_type_invalid_resource(self):
        test_resource = 'test'
        region_resource_id_status.config['allowed_resource_type'] = {}

        self.assertRaises(region_resource_id_status.InputError,
                          region_resource_id_status.validate_resource_type,
                          test_resource)

    @mock.patch.object(region_resource_id_status.factory, 'get_region_resource_id_status_connection')
    def test_get_regions_by_status_resource_id_sanity(self, mock_factory):
        # Make sure that no exception is raised
        region_resource_id_status.get_regions_by_status_resource_id(1, 2)

    @mock.patch.object(region_resource_id_status.factory, 'get_region_resource_id_status_connection')
    def test_get_status_by_resource_id_sanity(self, mock_factory):
        # Make sure that no exception is raised
        region_resource_id_status.get_status_by_resource_id(1)

    def test_add_status_sanity(self):
        test_resource = 'test'
        region_resource_id_status.config['allowed_resource_type'] = {test_resource: 'A'}
        test_status = 'test'
        region_resource_id_status.config['allowed_status_values'].add(test_status)
        test_operation = 'test'
        region_resource_id_status.config['allowed_operation_type'] = {test_operation: 'A'}

        temp_mock = MockClass(['test'])
        region_resource_id_status.factory.get_region_resource_id_status_connection = temp_mock
        region_resource_id_status.add_status({'timestamp': 1,
                                              'region': 2,
                                              'status': test_status,
                                              'transaction_id': 4,
                                              'resource_id': 5,
                                              'ord_notifier_id': 6,
                                              'error_msg': 7,
                                              'error_code': 8,
                                              'resource_operation': test_operation,
                                              'resource_type': test_resource})
        self.assertTrue(temp_mock.done)

    def test_add_status_no_regions(self):
        test_resource = 'test'
        region_resource_id_status.config['allowed_resource_type'] = {test_resource: 'A'}
        test_status = 'test'
        region_resource_id_status.config['allowed_status_values'].add(test_status)
        test_operation = 'test'
        region_resource_id_status.config['allowed_operation_type'] = {test_operation: 'A'}

        temp_mock = MockClass([])
        region_resource_id_status.factory.get_region_resource_id_status_connection = temp_mock
        region_resource_id_status.add_status({'timestamp': 1,
                                              'region': 2,
                                              'status': test_status,
                                              'transaction_id': 4,
                                              'resource_id': 5,
                                              'ord_notifier_id': 6,
                                              'error_msg': 7,
                                              'error_code': 8,
                                              'resource_operation': test_operation,
                                              'resource_type': test_resource})
        self.assertTrue(temp_mock.done)

    def test_add_status_input_error(self):
        test_resource = 'test'
        region_resource_id_status.config['allowed_resource_type'] = {test_resource: 'A'}
        test_status = 'test'
        region_resource_id_status.config['allowed_status_values'].add(test_status)
        test_operation = 'test'
        region_resource_id_status.config['allowed_operation_type'] = {test_operation: 'A'}

        temp_mock = MockClass([])
        region_resource_id_status.factory.get_region_resource_id_status_connection = temp_mock
        self.assertRaises(region_resource_id_status.InputError,
                          region_resource_id_status.add_status,
                          {'timestamp': 1, 'region': 2, 'status': 3,
                           'transaction_id': 4, 'resource_id': 5,
                           'ord_notifier_id': 6, 'error_msg': 7,
                           'error_code': 8, 'resource_operation': test_operation,
                           'resource_type': test_resource})

    def test_add_status_other_exception(self):
        test_status = 'test'
        region_resource_id_status.config['allowed_status_values'].add(test_status)

        temp_mock = MockClass([])
        region_resource_id_status.factory.get_region_resource_id_status_connection = temp_mock
        self.assertRaises(KeyError, region_resource_id_status.add_status,
                          {'timestamp': 1, 'region': 2, 'status': test_status,
                           'transaction_id': 4, 'resource_id': 5, 'ord_notifier_id': 6,
                           'error_msg': 7, 'error_code': 8, 'resource_type': 9})
