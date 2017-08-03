from ims.persistency.wsme import models
from ims.tests import FunctionalTest
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
        image = get_image_model()
        image.handle_region_group()

        self.assertEqual(len(image.regions), 3)

    def test_handle_group_not_found(self):
        models.get_regions_of_group = mock.MagicMock(return_value=None)
        image = get_image_model()

        self.assertRaises(models.ErrorStatus, image.handle_region_group,)


def get_image_model():
    """
    this function create a customer model object for testing
    :return: new customer object
    """

    image = models.Image(id='a', regions=[models.Region(name='r1', type='group')])

    return image
