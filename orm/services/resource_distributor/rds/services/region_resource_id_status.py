import logging
import sys

from orm.services.resource_distributor.rds.services.base import Error, InputError
from orm.services.resource_distributor.rds.storage import factory

logger = logging.getLogger(__name__)
config = {
    'max_interval_time': {
    },
    'allowed_status_values': {
    }
}

num_of_seconds_in_minute = 60
num_of_miliseconds_in_seconds = 1000


def add_status(data):
    logger.debug("add resource status timestamp [{}], region [{}], status [{}] "
                 ", transaction_id [{}] and resource_id [{}], ord_notifier_id [{}], "
                 "error message [{}], error code [{}] and "
                 "resource_extra_metadata [{}]".format(data['timestamp'],
                                                       data['region'],
                                                       data['status'],
                                                       data['transaction_id'],
                                                       data['resource_id'],
                                                       data['ord_notifier_id'],
                                                       data['error_msg'],
                                                       data['error_code'],
                                                       data.get('resource_extra_metadata', None)))

    try:
        validate_status_value(data['status'])
        validate_operation_type(data['resource_operation'])
        validate_resource_type(data['resource_type'])

        conn = factory.get_region_resource_id_status_connection()
        conn.add_update_status_record(data['timestamp'], data['region'], data['status'],
                                      data['transaction_id'], data['resource_id'],
                                      data['ord_notifier_id'], data['error_msg'],
                                      data['error_code'],
                                      data['resource_operation'],
                                      data.get('resource_extra_metadata'))
        # post_data_to_image(data)
    except Error as e:
        logger.exception("invalid inputs error")
        raise
    except Exception:
        logger.exception("Unexpected error: {}".format(sys.exc_info()[0]))
        raise


def get_status_by_resource_id(resource_id):
    logger.debug("get status by resource id %s " % resource_id)
    conn = factory.get_region_resource_id_status_connection()
    result = conn.get_records_by_resource_id(resource_id)
    return result


def get_regions_by_status_resource_id(status, resource_id):
    logger.debug("get regions by status %s for resource %s" % (status, resource_id))
    conn = factory.get_region_resource_id_status_connection()
    result = conn.get_records_by_resource_id_and_status(resource_id,
                                                        status)
    return result


def validate_resource_type(resource_type):
    allowed_resource_type = config['allowed_resource_type']
    if resource_type not in allowed_resource_type:
        logger.exception("status value is not valid: {}".format(resource_type))
        raise InputError("operation_type", resource_type)


def validate_operation_type(operation_type):
    allowed_operation_type = config['allowed_operation_type']
    if operation_type not in allowed_operation_type:
        logger.exception("status value is not valid: {}".format(operation_type))
        raise InputError("operation_type", operation_type)


def validate_status_value(status):
    allowed_status_values = config['allowed_status_values']
    if status not in allowed_status_values:
        logger.exception("status value is not valid: {}".format(status))
        raise InputError("status", status)


# def post_data_to_image(data):
#     if data['resource_type'] == "image":
#         logger.debug("send metadata {} to ims :- {} for region {}".format(
#             data['resource_extra_metadata'], data['resource_id'], data['region']))
#         # ims_proxy.send_image_metadata(data['resource_extra_metadata'], data['resource_id'], data['region'])
#     return
