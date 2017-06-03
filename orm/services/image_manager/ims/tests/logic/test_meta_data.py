from ims.logic import metadata_logic
from ims.tests import FunctionalTest
from ims.persistency.sql_alchemy.db_models import ImageRegion
from ims.persistency.wsme.models import MetadataWrapper, Metadata
from ims.persistency.wsme import models
import mock


class TestMetaData(FunctionalTest):
    """metadata uni tests."""

    def setUp(self):
        FunctionalTest.setUp(self)

    def tearDown(self):
        FunctionalTest.tearDown(self)

    @mock.patch.object(metadata_logic, 'di')
    def test_add_metadtat_sucess(self, metadta_mock):
        data_manager = get_data_maneger_mock_metadata(image_rec=True)
        metadta_mock.resolver.unpack.return_value = data_manager
        result = metadata_logic.add_metadata("id", "region", {})

    @mock.patch.object(metadata_logic, 'di')
    def test_add_metadtat_notfound(self, metadta_mock):
        data_manager = get_data_maneger_mock_metadata()
        metadta_mock.resolver.unpack.return_value = data_manager
        with self.assertRaises(metadata_logic.ErrorStatus):
            metadata_logic.add_metadata("id", "region", {})

    @mock.patch.object(metadata_logic, 'di')
    def test_add_metadtat_with_regions_success(self, metadta_mock):
        data_manager = get_data_maneger_mock_metadata(image_rec=True,
                                                      regions=[ImageRegion(region_name="region")])
        metadta_mock.resolver.unpack.return_value = data_manager
        metadata_logic.add_metadata("id", "region",
                                    MetadataWrapper(Metadata("1", "2", "3")))


def get_data_maneger_mock_metadata(image_rec=None, regions=[]):
    data_manager = mock.MagicMock()

    DataManager = mock.MagicMock()
    db_record = mock.MagicMock()
    sql_record = mock.MagicMock()

    sql_record.regions = regions
    db_record.get_image_by_id.return_value = None
    if image_rec:
        db_record.get_image_by_id.return_value = sql_record

    DataManager.get_record.return_value = db_record
    data_manager.return_value = DataManager
    return data_manager
