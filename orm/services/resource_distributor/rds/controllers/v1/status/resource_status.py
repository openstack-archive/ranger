"""handle post request module."""
import logging
import time

import wsme
from pecan import rest
from rds.controllers.v1.base import InputValueError, ClientSideError
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

from rds.controllers.v1.status import get_resource
from rds.services import region_resource_id_status as regionResourceIdStatus
from rds.services.base import InputError, ErrorMesage
from rds.utils import utils

logger = logging.getLogger(__name__)


class MetaData(wtypes.DynamicBase):
    """class method metadata input."""
    checksum = wsme.wsattr(wtypes.text, mandatory=True)
    virtual_size = wsme.wsattr(wtypes.text, mandatory=True)
    size = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, checksum=None, virtual_size=None, size=None):
        """

        :param checksum:
        :param virtual_size:
        :param size:
        """
        self.size = size
        self.checksum = checksum
        self.virtual_size = virtual_size

    def to_dict(self):
        return dict(size=self.size,
                    checksum=self.checksum,
                    virtual_size=self.virtual_size)


class ResourceData(wtypes.DynamicBase):
    """class method, handle json input."""

    resource_id = wsme.wsattr(wtypes.text, mandatory=True, name='resource-id')
    request_id = wsme.wsattr(wtypes.text, mandatory=True, name='request-id')
    resource_type = wsme.wsattr(wtypes.text, mandatory=True,
                                name='resource-type')
    resource_template_version = wsme.wsattr(wtypes.text, mandatory=True,
                                            name='resource-template-version')
    resource_template_type = wsme.wsattr(wtypes.text, mandatory=True,
                                         name='resource-template-type')
    resource_operation = wsme.wsattr(wtypes.text, mandatory=True,
                                     name='resource-operation')
    ord_notifier_id = wsme.wsattr(wtypes.text, mandatory=True,
                                  name='ord-notifier-id')
    region = wsme.wsattr(wtypes.text, mandatory=True)
    status = wsme.wsattr(wtypes.text, mandatory=True)
    error_code = wsme.wsattr(wtypes.text, mandatory=True, name='error-code')
    error_msg = wsme.wsattr(wtypes.text, mandatory=True, name='error-msg')
    resource_extra_metadata = wsme.wsattr(MetaData, mandatory=False)

    def __init__(self, resource_id="", request_id="", resource_type="",
                 resource_template_version="", resource_template_type="",
                 resource_operation="", ord_notifier_id="", region="",
                 status="", error_code="", error_msg="",
                 resource_extra_metadata=None):
        """init function.

        :param resource_id: uuid
        :param request_id:
        :param resource_type: customer, flavor, image...
        :param resource_template_version: version of heat
        :param resource_template_type:
        :param resource_operation: create, delete..
        :param ord_notifier_id:
        :param region: lcp's
        :param status: success, error, submitted
        :param error_code:
        :param error_msg: error message
        """
        self.resource_id = resource_id
        self.request_id = request_id
        self.resource_type = resource_type
        self.resource_template_version = resource_template_version
        self.resource_template_type = resource_template_type
        self.resource_operation = resource_operation
        self.ord_notifier_id = ord_notifier_id
        self.region = region
        self.status = status
        self.error_code = error_code
        self.error_msg = error_msg
        if resource_extra_metadata:
            self.resource_extra_metadata = resource_extra_metadata


class StatusInput(wtypes.DynamicBase):
    """class method, input json header."""

    rds_listener = wsme.wsattr(ResourceData, mandatory=True,
                               name='rds-listener')

    def __init__(self, rds_listener=ResourceData()):
        """init function.

        :param rds_listener: json header
        """
        self.rds_listener = rds_listener


class Status(rest.RestController):
    """post status controller."""

    resource = get_resource.GetResource()

    @wsexpose(None, body=StatusInput, status_code=201,
              rest_content_types='json')
    def post(self, status_input):
        """handle post request.

        :param status_input: json data
        :return: 201 created
        :description: get input json create dict and save dict to the DB
        if any validation fields fail will return input value error 400
        """
        logger.info("post status")
        logger.debug("parse json!")
        data_to_save = dict(
            timestamp=int(time.time())*1000,
            region=status_input.rds_listener.region,
            resource_id=status_input.rds_listener.resource_id,
            status=status_input.rds_listener.status,
            transaction_id=status_input.rds_listener.request_id,
            error_code=status_input.rds_listener.error_code,
            error_msg=status_input.rds_listener.error_msg,
            resource_operation=status_input.rds_listener.resource_operation,
            resource_type=status_input.rds_listener.resource_type,
            ord_notifier_id=status_input.rds_listener.ord_notifier_id)

        if status_input.rds_listener.resource_type == 'image' and status_input.rds_listener.resource_extra_metadata != wsme.Unset:
            data_to_save['resource_extra_metadata'] =\
                status_input.rds_listener.resource_extra_metadata.to_dict()

        logger.debug("save data to database.. data :- %s" % data_to_save)
        try:
            regionResourceIdStatus.add_status(data_to_save)
            # send data to ims
            utils.post_data_to_image(data_to_save)
        except ErrorMesage as exp:
            logger.error(exp.message)
            # raise ClientSideError(status_code=400, error=exp.message)
        except InputError as e:
            logger.error("Invalid value for input {}: {}".format(str(e.name),
                                                                 str(e.value)))
            raise InputValueError(e.name, e.value)
