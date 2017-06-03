import unittest

from rds.storage.region_resource_id_status import Base


class BaseStorageTests(unittest.TestCase):

    def test_storage_add_status_record_not_implemented(self):
        """ Check if creating an instance and calling add_update_status_record method fail"""
        with self.assertRaises(Exception):
            Base("").add_update_status_record('1','2','3','4','5','6','7','8')

    def test_storage_get_records_by_resource_id_implemented(self):
        """ Check if creating an instance and calling get_records_by_resource_id method fail"""
        with self.assertRaises(Exception):
            Base("").get_records_by_resource_id('1')

    def test_storage_get_records_by_filter_args_implemented(self):
        """ Check if creating an instance and calling get_records_by_filter_args method fail"""
        with self.assertRaises(Exception):
            Base("").get_records_by_filter_args(abc="def")
