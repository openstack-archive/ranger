import mock
from fms_rest.tests import FunctionalTest

from fms_rest.data.wsme import models

GROUP_REGIONS = [
    "DPK",
    "SNA1",
    "SNA2"
]


class TestModels(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        models.get_regions_of_group = mock.MagicMock(return_value=GROUP_REGIONS)
        models.set_utils_conf = mock.MagicMock()

    def test_handle_group_success(self):
        flavor = get_flavor_model()
        flavor.handle_region_groups()

        self.assertEqual(len(flavor.regions), 3)

    def test_handle_group_not_found(self):
        models.get_regions_of_group = mock.MagicMock(return_value=None)
        flavor = get_flavor_model()

        self.assertRaises(ValueError, flavor.handle_region_groups,)


def get_flavor_model():
    """
    this function create a customer model object for testing
    :return: new customer object
    """

    flavor = models.Flavor(id='1', regions=[models.Region(name='r1', type='group')])

    return flavor
