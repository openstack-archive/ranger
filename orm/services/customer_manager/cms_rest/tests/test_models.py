from cms_rest.model import Models as models
from cms_rest.tests import FunctionalTest
import mock

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
        cust = get_cust_model()
        cust.handle_region_group()

        self.assertEqual(len(cust.regions), 3)

    def test_handle_group_not_found(self):
        models.get_regions_of_group = mock.MagicMock(return_value=None)
        cust = get_cust_model()

        self.assertRaises(models.ErrorStatus, cust.handle_region_group,)


def get_cust_model():
    """this function create a customer model object for testing
    :return: new customer object
    """

    cust = models.Customer(enabled=False,
                           name='a',
                           metadata={'a': 'b'},
                           regions=[models.Region(name='r1',
                                                  type='group',
                                                  quotas=[models.Quota()],
                                                  users=[models.User(id='a', role=['admin'])])],
                           users=[models.User(id='b', role=['admin'])],
                           defaultQuotas=[models.Quota()])

    return cust
