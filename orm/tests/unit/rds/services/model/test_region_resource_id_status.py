import unittest

from orm.services.resource_distributor.rds.services.model import region_resource_id_status


class TestModel(unittest.TestCase):
    def test_model_as_dict(self):
        model = region_resource_id_status.Model(1, 2, 3, 4, 5, 6, 7, 8,
                                                'create')
        expected_dict = {
            'timestamp': 1,
            'region': 2,
            'status': 3,
            'ord_transaction_id': 4,
            'resource_id': 5,
            'ord_notifier_id': 6,
            'error_msg': 7,
            'error_code': 8,
            'operation': 'create',
            'resource_extra_metadata': None
        }

        test_dict = model.as_dict()
        self.assertEqual(test_dict, expected_dict)


class TestStatusModel(unittest.TestCase):
    def test_get_aggregated_status_error(self):
        model = region_resource_id_status.Model(1, 2, 'Error', 4, 5, 6, 7, 8,
                                                'create')
        status_model = region_resource_id_status.StatusModel([model])
        self.assertEqual(status_model.status, 'Error')

    def test_get_aggregated_status_pending(self):
        model = region_resource_id_status.Model(1, 2, 'Submitted', 4, 5, 6, 7,
                                                8, 'create')
        status_model = region_resource_id_status.StatusModel([model])
        self.assertEqual(status_model.status, 'Pending')

    def test_get_aggregated_status_success(self):
        model = region_resource_id_status.Model(1, 2, 'Success', 4, 5, 6, 7, 8,
                                                'create')
        status_model = region_resource_id_status.StatusModel([model])
        self.assertEqual(status_model.status, 'Success')
