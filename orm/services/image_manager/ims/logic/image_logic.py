from ims.logger import get_logger
from ims.persistency.wsme.models import ImageWrapper, ImageSummaryResponse
from ims.persistency.wsme.models import Region, ImageSummary, RegionWrapper
from ims.persistency.sql_alchemy.db_models import ImageRegion, ImageCustomer
from ims.logic.error_base import ErrorStatus, NotFoundError, NoContentError
from ims.utils import utils as ImsUtils

from orm_common.utils import utils
from orm_common.injector import injector
import time

from pecan import request, conf

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('data_manager')
def create_image(image_wrapper, image_uuid, transaction_id):
    DataManager = di.resolver.unpack(create_image)
    datamanager = DataManager()

    image_wrapper.image.id = image_uuid

    image_wrapper.image.created_at = str(int(time.time()))
    image_wrapper.image.updated_at = image_wrapper.image.created_at

    try:
        image_wrapper.handle_region_group()
        image_wrapper.validate_model()
        sql_image = image_wrapper.to_db_model()

        image_rec = datamanager.get_record('image')

        datamanager.begin_transaction()
        image_rec.insert(sql_image)
        datamanager.flush()  # i want to get any exception created by this
        # insert
        existing_region_names = []
        send_to_rds_if_needed(sql_image, existing_region_names, "post",
                              transaction_id)

        datamanager.commit()

        ret_image = get_image_by_uuid(image_uuid)
        return ret_image

    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to CreateImage", exp)
        datamanager.rollback()
        raise


@di.dependsOn('rds_proxy')
def send_to_rds_if_needed(sql_image, existing_region_names, http_action,
                          transaction_id):
    rds_proxy = di.resolver.unpack(send_to_rds_if_needed)
    if (sql_image.regions and len(sql_image.regions) > 0) or len(
            existing_region_names) > 0:
        image_dict = sql_image.get_proxy_dict()
        update_region_actions(image_dict, existing_region_names, http_action)
        if image_dict['regions'] or len(existing_region_names) > 0:
            LOG.debug("Image is valid to send to RDS - sending to RDS Proxy ")
            rds_proxy.send_image(image_dict, transaction_id, http_action)
        else:
            LOG.debug("Group with no regions - wasn't send to RDS Proxy " + str(
                sql_image))
    else:
        LOG.debug("Image with no regions - wasn't send to RDS Proxy " + str(
            sql_image))


@di.dependsOn('data_manager')
def update_image(image_wrapper, image_uuid, transaction_id, http_action="put"):
    DataManager = di.resolver.unpack(update_image)
    datamanager = DataManager()

    try:
        image_wrapper.validate_model('update')
        new_image = image_wrapper.to_db_model()
        new_image.id = image_uuid

        datamanager.begin_transaction()

        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)

        if sql_image is None:
            raise NotFoundError(status_code=404,
                                message="Image {0} does not exist for update".format(
                                    image_uuid))

        new_image.owner = sql_image.owner
        existing_regions = sql_image.get_existing_region_names()
        new_image.created_at = int(sql_image.created_at)
        new_image.updated_at = int(time.time())
        # result = image_rec.delete_image_by_id(image_uuid)
        datamanager.get_session().delete(sql_image)
        # del sql_image
        image_rec.insert(new_image)
        datamanager.flush()

        send_to_rds_if_needed(new_image, existing_regions, http_action,
                              transaction_id)

        datamanager.commit()

        ret_image = get_image_by_uuid(image_uuid)

        return ret_image

    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("ImageLogic - Failed to update image", exp)
        raise


@di.dependsOn('rds_proxy')
@di.dependsOn('data_manager')
def delete_image_by_uuid(image_uuid, transaction_id):
    rds_proxy, DataManager = di.resolver.unpack(delete_image_by_uuid)
    datamanager = DataManager()

    try:

        datamanager.begin_transaction()
        image_rec = datamanager.get_record('image')

        sql_image = image_rec.get_image_by_id(image_uuid)
        if sql_image is None:
            return

        image_existing_region_names = sql_image.get_existing_region_names()
        if len(image_existing_region_names) > 0:
            # Do not delete a flavor that still has some regions
            raise ErrorStatus(405,
                              "Cannot delete a image with regions. "
                              "Please delete the regions first and then "
                              "delete the image. ")

        # Get status from RDS
        image_status = rds_proxy.get_status(sql_image.id, False)

        status_resp = None

        if image_status.status_code == 200:
            status_resp = image_status.json()['status']
            LOG.debug('RDS returned status: {}'.format(status_resp))

        elif image_status.status_code == 404:
            status_resp = 'Success'

        else:
            # fail to get status from rds
            raise ErrorStatus(500, "fail to get status for this resource "
                                   "deleting image not allowed ")

        if status_resp != 'Success':
            raise ErrorStatus(405, "not allowed as aggregate status "
                                   "have to be Success (either the deletion"
                                   " failed on one of the regions or it is "
                                   "still in progress)")

        image_rec.delete_image_by_id(image_uuid)
        datamanager.flush()  # i want to get any exception created by this

        # delete
        datamanager.commit()

    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to delete image", exp)
        datamanager.rollback()
        raise


@di.dependsOn('data_manager')
def add_regions(image_uuid, regions, transaction_id):
    DataManager = di.resolver.unpack(add_regions)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)
        if not sql_image:
            raise ErrorStatus(404, 'image with id: {0} not found'.format(
                image_uuid))

        existing_region_names = sql_image.get_existing_region_names()

        for region in regions.regions:
            db_region = ImageRegion(region_name=region.name, region_type=region.type)
            sql_image.add_region(db_region)

        datamanager.flush()  # i want to get any exception created by
        # previous actions against the database

        send_to_rds_if_needed(sql_image, existing_region_names, "put",
                              transaction_id)

        datamanager.commit()

        image_wrapper = get_image_by_uuid(image_uuid)
        ret = RegionWrapper(regions=image_wrapper.image.regions)
        return ret

    except ErrorStatus as exp:
        LOG.log_exception("ImageLogic - Failed to add regions", exp)
        datamanager.rollback()
        raise exp
    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to add regions", exp)
        datamanager.rollback()
        raise exp


@di.dependsOn('data_manager')
def replace_regions(image_uuid, regions, transaction_id):
    DataManager = di.resolver.unpack(replace_regions)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)
        if not sql_image:
            raise ErrorStatus(404, 'image with id: {0} not found'.format(
                image_uuid))

        existing_region_names = sql_image.get_existing_region_names()

        sql_image.remove_all_regions()
        datamanager.flush()

        for region in regions.regions:
            db_region = ImageRegion(region_name=region.name, region_type=region.type)
            sql_image.add_region(db_region)
        datamanager.flush()  # i want to get any exception created by
        # previous actions against the database

        send_to_rds_if_needed(sql_image, existing_region_names, "put",
                              transaction_id)

        datamanager.commit()

        image_wrapper = get_image_by_uuid(image_uuid)
        ret = RegionWrapper(regions=image_wrapper.image.regions)
        return ret

    except ErrorStatus as exp:
        LOG.log_exception("ImageLogic - Failed to replace regions", exp)
        datamanager.rollback()
        raise exp
    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to repalce regions", exp)
        datamanager.rollback()
        raise exp


@di.dependsOn('data_manager')
def delete_region(image_uuid, region_name, transaction_id):
    DataManager = di.resolver.unpack(delete_region)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)
        if not sql_image:
            raise ErrorStatus(404, 'image with id: {0} not found'.format(
                image_uuid))

        existing_region_names = sql_image.get_existing_region_names()

        sql_image.remove_region(region_name)

        datamanager.flush()  # i want to get any exception created by
        # previous actions against the database
        send_to_rds_if_needed(sql_image, existing_region_names, "put",
                              transaction_id)

        datamanager.commit()

    except ErrorStatus as exp:
        LOG.log_exception("ImageLogic - Failed to update image", exp)
        datamanager.rollback()
        raise

    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to delete region", exp)
        datamanager.rollback()
        raise


@di.dependsOn('data_manager')
def add_customers(image_uuid, customers, transaction_id):
    DataManager = di.resolver.unpack(add_customers)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)
        if not sql_image:
            raise ErrorStatus(404, 'image with id: {0} not found'.format(
                image_uuid))

        if sql_image.visibility == "public":
            raise ErrorStatus(400, 'Cannot add Customers to public Image')

        existing_region_names = sql_image.get_existing_region_names()

        for user in customers.customers:
            db_Customer = ImageCustomer(customer_id=user)
            sql_image.add_customer(db_Customer)

        datamanager.flush()  # i want to get any exception created by
        # previous actions against the database
        send_to_rds_if_needed(sql_image, existing_region_names, "put",
                              transaction_id)
        datamanager.commit()

        ret_image = get_image_by_uuid(image_uuid)
        return ret_image

    except Exception as exp:
        if 'conflicts with persistent instance' in exp.message or 'Duplicate entry' in exp.message:
            raise ErrorStatus(409, "Duplicate Customer for Image")
        LOG.log_exception("ImageLogic - Failed to add Customers", exp)
        datamanager.rollback()
        raise


@di.dependsOn('data_manager')
def replace_customers(image_uuid, customers, transaction_id):
    DataManager = di.resolver.unpack(replace_customers)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)
        if not sql_image:
            raise ErrorStatus(404, 'image {0} not found'.format(image_uuid))

        if sql_image.visibility == "public":
            raise ValueError('Cannot add Customers to public Image')

        existing_region_names = sql_image.get_existing_region_names()
        sql_image.remove_all_customers()
        datamanager.flush()

        for cust in customers.customers:
            db_Customer = ImageCustomer(customer_id=cust)
            sql_image.add_customer(db_Customer)

        datamanager.flush()  # get exception created by previous db actions
        send_to_rds_if_needed(sql_image, existing_region_names, "put",
                              transaction_id)
        datamanager.commit()

        ret_image = get_image_by_uuid(image_uuid)
        return ret_image

    except Exception as exp:
        if 'conflicts with persistent instance' in exp.message or 'Duplicate entry' in exp.message:
            raise ErrorStatus(409, "Duplicate Customer for Image")
        LOG.log_exception("ImageLogic - Failed to add Customers", exp)
        datamanager.rollback()
        raise


@di.dependsOn('data_manager')
def delete_customer(image_uuid, customer_id, transaction_id):
    DataManager = di.resolver.unpack(delete_customer)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)
        if not sql_image:
            raise ErrorStatus(404, 'image {0} not found'.format(image_uuid))
        # if trying to delete the only one Customer then return value error
        if sql_image.visibility == "public":
            raise ValueError("Image {} is public, no customers".format(image_uuid))

        if len(sql_image.customers) == 1 and \
                sql_image.customers[0].customer_id == customer_id:
            raise ValueError('Private Image must have at least one Customer - '
                             'You are trying to delete the only one Customer')

        existing_region_names = sql_image.get_existing_region_names()
        sql_image.remove_customer(customer_id)

        datamanager.flush()  # i want to get any exception created by
        # previous actions against the database
        send_to_rds_if_needed(sql_image, existing_region_names, "put",
                              transaction_id)
        datamanager.commit()

    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to delete Customer", exp)
        datamanager.rollback()
        raise


@di.dependsOn('data_manager')
@di.dependsOn('rds_proxy')
def get_image_by_uuid(image_uuid):
    DataManager, rds_proxy = di.resolver.unpack(get_image_by_uuid)
    datamanager = DataManager()

    LOG.debug("Get image by uuid : {}".format(image_uuid))
    try:

        datamanager.begin_transaction()

        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image_by_id(image_uuid)

        if not sql_image:
            raise NotFoundError(status_code=404,
                                message="Image {0} not found ".format(
                                    image_uuid))

        image_wrapper = ImageWrapper.from_db_model(sql_image)

        # get image own link
        image_wrapper.image.links, image_wrapper.image.self_link = ImsUtils.get_server_links(image_uuid)
        # convert time stamp format to human readable time
        image_wrapper.image.created_at = ImsUtils.convert_time_human(
            image_wrapper.image.created_at)
        image_wrapper.image.updated_at = ImsUtils.convert_time_human(
            image_wrapper.image.updated_at)
        # Get the status from RDS
        image_status = rds_proxy.get_status(image_wrapper.image.id, False)

        if image_status.status_code != 200:
            return image_wrapper
        image_status = image_status.json()
        image_wrapper.image.status = image_status['status']
        # update status for all regions
        for result_regions in image_wrapper.image.regions:
            for status_region in image_status['regions']:
                if result_regions.name == status_region['region']:
                    result_regions.status = status_region['status']

    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("ImageLogic - Failed to update image", exp)
        raise exp

    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("ImageLogic - Failed to delete Customer", exp)
        raise

    return image_wrapper


@di.dependsOn('data_manager')
def get_image_list_by_params(visibility, region, Customer):
    DataManager = di.resolver.unpack(get_image_list_by_params)

    datamanager = DataManager()
    try:
        image_record = datamanager.get_record('image')
        sql_images = image_record.get_images_by_criteria(visibility=visibility,
                                                         region=region,
                                                         Customer=Customer)

        response = ImageSummaryResponse()
        for sql_image in sql_images:
            image = ImageSummary.from_db_model(sql_image)
            response.images.append(image)

        return response

    except ErrorStatus as exp:
        LOG.log_exception("ImageLogic - Failed to get list", exp)
        raise
    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to get list", exp)
        raise


def update_region_actions(image_dict, existing_region_names, action="put"):
    if action == "delete":
        set_regions_action(image_dict, "delete")
    elif action == "post":
        set_regions_action(image_dict, "create")
    else:  # put
        for region in image_dict["regions"]:
            if region["name"] in existing_region_names:
                region["action"] = "modify"
            else:
                region["action"] = "create"

        # add deleted regions
        for exist_region_name in existing_region_names:
            if region_name_exist_in_regions(exist_region_name,
                                            image_dict["regions"]):
                continue
            else:
                image_dict["regions"].append(
                    {"name": exist_region_name, "action": "delete"})


def region_name_exist_in_regions(region_name, regions):
    for region in regions:
        if region["name"] == region_name:
            return True
    return False


def set_regions_action(image_dict, action):
    for region in image_dict["regions"]:
        region["action"] = action


@di.dependsOn('data_manager')
def enable_image(image_uuid, int_enabled, transaction_id):
    DataManager = di.resolver.unpack(enable_image)
    datamanager = DataManager()

    try:
        image_rec = datamanager.get_record('image')
        sql_image = image_rec.get_image(image_uuid)
        if not sql_image:
            raise ErrorStatus(404, 'Image with id: {0} not found'.format(
                image_uuid))

        sql_image.enabled = int_enabled

        existing_region_names = sql_image.get_existing_region_names()

        datamanager.flush()  # i want to get any exception created by this
        # insert method

        send_to_rds_if_needed(sql_image, existing_region_names, "put",
                              transaction_id)

        datamanager.commit()

        ret_image = get_image_by_uuid(image_uuid)
        return ret_image

    except ErrorStatus as exp:
        LOG.log_exception("ImageLogic - Failed to change image activation value", exp)
        datamanager.rollback()
        raise exp
    except Exception as exp:
        LOG.log_exception("ImageLogic - Failed to change image activation value", exp)
        datamanager.rollback()
        raise exp
