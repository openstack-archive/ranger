from orm.services.image_manager.ims.persistency.wsme import models
from orm.tests.unit.ims import FunctionalTest

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


class TestWsmeModels(FunctionalTest):
    def test_create_image_visibility(self):
        image_wrapper = models.ImageWrapper()
        image_wrapper.image = models.Image()

        image_wrapper.image.name = 'name'
        image_wrapper.image.url = 'http://aic.att.com'
        image_wrapper.image.visibility = 'private'
        image_wrapper.image.disk_format = 'raw'
        image_wrapper.image.container_format = 'bare'
        image_wrapper.image.min_ram = 1024
        image_wrapper.image.customers = ['a1', 'a2']

        sql_image = image_wrapper.validate_model()

        self.assertEqual(len(image_wrapper.image.customers), 2)


def get_image_model():
    """this function create a customer model object for testing
    :return: new customer object
    """

    image = models.Image(id='a', regions=[models.Region(name='r1', type='group')])

    return image
