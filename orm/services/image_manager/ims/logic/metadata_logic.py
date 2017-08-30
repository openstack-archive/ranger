from orm.common.orm_common.injector import injector
from orm.services.image_manager.ims.logger import get_logger
from orm.services.image_manager.ims.logic.error_base import ErrorStatus

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('data_manager')
def add_metadata(image_id, region_name, metadata_wrapper):
    DataManager = di.resolver.unpack(add_metadata)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_id)
        if not sql_image:
            raise ErrorStatus(404, 'image {0} not found'.format(image_id))

        for region in sql_image.regions:
            if region.region_name == region_name:
                region.checksum = metadata_wrapper.metadata.checksum
                region.size = metadata_wrapper.metadata.size
                region.virtual_size = metadata_wrapper.metadata.virtual_size

        datamanager.flush()
        datamanager.commit()

    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to add regions", exp)
        datamanager.rollback()
        raise
