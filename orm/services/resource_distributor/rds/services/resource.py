"""create resource moudle."""
import logging
import time

from orm.services.resource_distributor.rds.services import region_resource_id_status as regionResourceIdStatus
from orm.services.resource_distributor.rds.services import (yaml_customer_builder, yaml_flavor_bulder,
                                                            yaml_image_builder)
from orm.services.resource_distributor.rds.services.base import ConflictValue, ErrorMessage
from orm.services.resource_distributor.rds.services.model.resource_input import ResourceData as InputData
from orm.services.resource_distributor.rds.sot import sot_factory
from orm.services.resource_distributor.rds.utils import utils, uuid_utils


from pecan import conf, request

my_logger = logging.getLogger(__name__)


def _get_inputs_from_resource_type(jsondata,
                                   resource_type,
                                   external_transaction_id,
                                   operation="create"):
    if resource_type == "customer":
        input_data = InputData(resource_id=jsondata['uuid'],
                               resource_type=resource_type,
                               operation=operation,
                               targets=jsondata['regions'],
                               model=jsondata,
                               external_transaction_id=external_transaction_id)
    elif resource_type == "flavor" or resource_type == "image":
        input_data = InputData(resource_id=jsondata['id'],
                               resource_type=resource_type,
                               operation=operation,
                               targets=jsondata['regions'],
                               model=jsondata,
                               external_transaction_id=external_transaction_id)
    else:
        raise ErrorMessage("no support for resource %s" % resource_type)
    return input_data


def _region_valid(region):
    if 'rms_status' in region and region[
            'rms_status'] not in conf.allow_region_statuses:
        return False
    return True


def _create_or_update_resource_status(input_data, target, error_msg='',
                                      status="Submitted"):
    # check rms region status
    if not _region_valid(target):
        status = 'Error'
        error_msg = "Not sent to ord as status equal to " + target['rms_status']
        raise ErrorMessage("Not sent to ord as status equal to %s"
                           % target['rms_status'])

    my_logger.debug("save status as %s" % status)
    data_to_save = dict(
        timestamp=int(time.time() * 1000),
        region=target['name'],
        resource_id=input_data.resource_id,
        status=status,
        transaction_id=input_data.transaction_id,
        error_code='',
        error_msg=error_msg,
        resource_operation=target['action'],
        resource_type=input_data.resource_type,
        ord_notifier_id='')
    regionResourceIdStatus.add_status(data_to_save)
    my_logger.debug("status %s saved" % status)


def _set_all_statuses_to_error(input_data, message=None):
    targets = input_data.targets
    for target in targets:
        _create_or_update_resource_status(input_data=input_data, target=target,
                                          error_msg=message or 'system error',
                                          status="Error")


def _create_data_to_sot(input_data):
    """create data.

    : build yaml string
    :param jsondata: full json in request body
    :param resource_type: eg... Customer
    :return: return list of dictionaries with yaml string
    """
    jsondata = input_data.model
    targetslist = []
    create_req = False
    targets = input_data.targets
    for target in targets:
        # save start status to submitted for each region
        _create_or_update_resource_status(input_data, target)
        if not _region_valid(target):
            continue
        if target['action'] == "delete":
            yamldata = "delete"
        elif input_data.resource_type == "customer":
            yamldata = yaml_customer_builder.yamlbuilder(jsondata, target)
        elif input_data.resource_type == "flavor":
            yamldata = yaml_flavor_bulder.yamlbuilder(jsondata, target)
        elif input_data.resource_type == "image":
            if target['action'] == "create":
                create_req = True
            yamldata = yaml_image_builder.yamlbuilder(jsondata, target,
                                                      create_req)
        targetslist.append({"region_id": target['name'],
                            "resource_type": input_data.resource_type,
                            "resource_name": input_data.resource_id,
                            "template_data": yamldata,
                            "operation": target['action']})
    return targetslist


def _upload_to_sot(uuid, tranid, targetslist):
    application_id = request.headers[
        'X-RANGER-Client'] if 'X-RANGER-Client' in request.headers else \
        'NA'
    user_id = request.headers[
        'X-RANGER-Requester'] if 'X-RANGER-Requester' in request.headers else \
        ''
    sot = sot_factory.get_sot()
    sot.save_resource_to_sot(uuid,
                             tranid,
                             targetslist,
                             application_id,
                             user_id)


def _check_resource_status(input_data):
    resource_id = input_data.resource_id
    status = conf.block_by_status
    # check if any of the region creation in pending
    regions_by_resource = \
        regionResourceIdStatus.get_regions_by_status_resource_id(status,
                                                                 resource_id)
    # if any not ready return 409
    if regions_by_resource is not None and regions_by_resource.regions:
        raise ConflictValue([region.region for region in regions_by_resource.regions])


def update_sot(input_data):
    """create resource."""
    my_logger.debug("build yaml file for %s id: %s" % (input_data.resource_type,
                    input_data.resource_id))
    targetslist = _create_data_to_sot(input_data)
    my_logger.debug("upload yaml to SoT")
    _upload_to_sot(input_data.resource_id,
                   input_data.transaction_id,
                   targetslist)


def main(jsondata, external_transaction_id, resource_type, operation):
    """main function handle resource operation."""
    my_logger.info("got %s for %s resource" % (operation, resource_type))
    try:
        input_data = _get_inputs_from_resource_type(
            jsondata=jsondata,
            resource_type=resource_type,
            operation=operation,
            external_transaction_id=external_transaction_id
        )
        my_logger.debug("iterate through the regions see if none in submitted")
        _check_resource_status(input_data)
        my_logger.debug("get uuid from uuid generator")
        input_data.transaction_id = uuid_utils.get_random_uuid()
        my_logger.debug("uuid ={}".format(input_data.transaction_id))
        # add regions status from rms (to check if it down)
        input_data.targets = utils.add_rms_status_to_regions(
            input_data.targets, input_data.resource_type)
        update_sot(input_data)
    except ConflictValue:
        raise
    except ErrorMessage as exp:
        my_logger.error(exp.message)
        my_logger.exception(exp)
        raise
    except Exception as e:
        my_logger.exception(e)
        _set_all_statuses_to_error(input_data)
        my_logger.error("deleting fails ,Error : {}".format(str(e.message)))
        raise ErrorMessage(str(e.message))
    return input_data.resource_id
