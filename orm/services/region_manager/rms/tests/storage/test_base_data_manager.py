import unittest

from rms.storage.base_data_manager import BaseDataManager


class BaseDataManagerTests(unittest.TestCase):

    def test_base_data_manager_add_region_not_implemented(self):
        """ Check if creating an instance and calling add_region
        method fail
        """
        with self.assertRaises(NotImplementedError):
            BaseDataManager("", "", "").add_region('1', '2', '3', '4', '5', '6', '7',
                                                   '8', '9', '10', '11', '12', '13',
                                                   '14', '15', '16', '17')

    def test_base_data_manager_get_regions_not_implemented(self):
        """ Check if creating an instance and calling get_regions
        method fail
        """
        with self.assertRaises(NotImplementedError):
            BaseDataManager("", "", "").get_regions('1', '2', '3')

    def test_base_data_manager_get_all_regions_not_implemented(self):
        """ Check if creating an instance and calling get_all_regions
        method fail
        """
        with self.assertRaises(NotImplementedError):
            BaseDataManager("", "", "").get_all_regions()

    def test_base_data_manager_add_group_not_implemented(self):
        """ Check if creating an instance and calling add_group
        method fail
        """
        with self.assertRaises(NotImplementedError):
            BaseDataManager("", "", "").add_group("1", "2", "3", "4")

    def test_base_data_manager_get_group_not_implemented(self):
        """ Check if creating an instance and calling get_group
        method fail
        """
        with self.assertRaises(NotImplementedError):
            BaseDataManager("", "", "").get_group("1")

    def test_base_data_manager_get_all_groups_not_implemented(self):
        """ Check if creating an instance and calling get_all_groups
        method fail
        """
        with self.assertRaises(NotImplementedError):
            BaseDataManager("", "", "").get_all_groups()
