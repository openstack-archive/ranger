import unittest

from rds.sot.base_sot import BaseSoT


class BaseSoTTests(unittest.TestCase):

    def test_base_sot_no_method_save_implemented(self):
        """ Check if creating an instance and calling save method fail"""
        with self.assertRaises(Exception):
            sot = BaseSoT()
            sot.save_resource_to_sot('1','2',[])

    def test_base_sot_no_method_validate_implemented(self):
        """ Check if creating an instance and calling validate method fail"""
        with self.assertRaises(Exception):
            sot = BaseSoT()
            sot.validate_sot_state()


