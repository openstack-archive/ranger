import os
import traceback

from ims.logger import get_logger
from ims.persistency.sql_alchemy.data_manager import DataManager
from ims.persistency.sql_alchemy.db_models import (Image, ImageCustomer,
                                                   ImageProperty, ImageRegion)
from pecan import conf
from pecan.testing import load_test_app

# conf = imp.load_source('config.py', '../config.py')


image_id = "Id 11"  # image id

LOG = get_logger(__name__)


def main():
    try:
        # prepare_service()

        print conf.database

        data_manager = DataManager()

        image_record = data_manager.get_record("Image")

        image = image_record.get_image(image_id)

        print image.regions
        print image.properties

        all_images = image_record.get_all_images(start=0, limit=50)
        print all_images

        # LOG.debug("TestDatabase finished well")

    except Exception as exception:
        print("Exception" + str(exception))
        # LOG.error("Exception in TestDatabase: " + str(exception))


def delete():
    try:
        # prepare_service()

        print conf.database

        data_manager = DataManager()

        image_record = data_manager.get_record("Image")

        data_manager.begin_transaction()

        result = image_record.delete_by_id(image_id)

        data_manager.commit()
        print "Nm records deleted: " + str(result.rowcount)
        # LOG.debug("TestDatabase finished well")

    except Exception as exception:
        print("Exception" + str(exception))

        # LOG.error("Exception in TestDatabase: " + str(exception))


def main2():
    # get customer by id of 1
    try:
        # prepare_service()

        data_manager = DataManager()

        image_record = data_manager.get_record("Image")

        criterias = {"visibility": "public", "region": "North", "tenant": "Tenanat-1", "start": 0, "limit": 10,
                     "profile": "NS"}
        images = image_record.get_images_by_criteria(**criterias)

        print len(images)

    except Exception as exception:
        LOG.log_exception("Failed to get_images_by_criteria: ", exception)
        # log_exception(LOG, "Failed to read customer: 10", exception)
        # log_exception("Failed to read customer: 10", exception)
        # LOG.error("Exception in TestDatabase: " + str(exception))
        # print_exception(exception)


def main3():
    try:
        # prepare_service()

        print conf.database

        data_manager = DataManager()

        image_record = data_manager.get_record("Image")

        image = image_record.get_image(image_id)

        print image.image_extra_specs
        print image.image_regions
        print image.image_tenants

        region = ImageRegion(region_name="Israel")
        image.add_region(region)

        region = ImageRegion(region_name="Israel2")
        image.add_region(region)

        tenant = ImageCustomer(tenant_id="Zion")
        image.add_tenant(tenant)

        tenant = ImageCustomer(tenant_id="Zion2")
        image.add_tenant(tenant)

        data_manager.commit()

        # LOG.debug("TestDatabase finished well")

    except Exception as exception:
        print("Exception" + str(exception))
        # LOG.error("Exception in TestDatabase: " + str(exception))


def main4():
    try:
        # prepare_service()

        print conf.database

        data_manager = DataManager()

        image_record = data_manager.get_record("Image")

        image = image_record.get_image(image_id)

        print image.image_extra_specs
        print image.image_regions
        print image.image_tenants

        image.remove_region("Israel")
        image.remove_region("Israel2")

        image.remove_tenant("Zion")
        image.remove_tenant("Zion2")

        data_manager.commit()

        # LOG.debug("TestDatabase finished well")

    except Exception as exception:
        print("Exception" + str(exception))
        # LOG.error("Exception in TestDatabase: " + str(exception))


def insert_data():
    try:
        # prepare_service()

        print conf.database

        data_manager = DataManager()

        image_record = data_manager.get_record("Image")

        image_property1 = ImageProperty(key_name="key_1", key_value="key_valu1")
        image_property2 = ImageProperty(key_name="key_2", key_value="key_valu2")
        image_property3 = ImageProperty(key_name="key_3", key_value="key_valu3")

        image_region1 = ImageRegion(region_name="region1", region_type="single")
        image_region2 = ImageRegion(region_name="region2", region_type="single")

        image = Image(name="Name1",
                      id="Id 10",
                      enabled=1,
                      protected="protected",
                      url="Http:\\zion.com",
                      visibility="puplic",
                      disk_format="disk format",
                      container_format="container_format",
                      min_disk=512,
                      owner="zion",
                      schema="big_data",
                      min_ram=1)

        image.properties.append(image_property1)
        image.properties.append(image_property2)
        image.properties.append(image_property3)
        image.regions.append(image_region1)
        image.regions.append(image_region2)
        image_record.insert(image)

        data_manager.commit()

        # LOG.debug("TestDatabase finished well")

    except Exception as exception:
        print("Exception" + str(exception))
        # LOG.error("Exception in TestDatabase: " + str(exception))


def print_exception():
    try:
        print "*** print_exc:"
        traceback.print_exc()
        print "*** format_exception:"
        print traceback.format_exc()
        print "*** extract_tb:"
        print traceback.extract_tb()
        print "*** format_tb:"
        print traceback.format_tb()
    except Exception as exception1:
        print "*** print_exc:"
        traceback.print_exc()


if __name__ == "__main__":
    app = load_test_app(os.path.join(
        os.path.dirname(__file__),
        './config.py'
    ))

    # main()
    insert_data()
    delete()
    # main4()
