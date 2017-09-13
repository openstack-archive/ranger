"""handle get resource module."""
import logging

from orm.services.resource_distributor.rds.controllers.v1.base import EntityNotFoundError
from orm.services.resource_distributor.rds.services import region_resource_id_status as regionResourceIdStatus

from pecan import rest
import wsme
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

logger = logging.getLogger(__name__)


class ResourceMetaData(wtypes.DynamicBase):
    """class method."""

    checksum = wsme.wsattr(wtypes.text, mandatory=True)
    virtual_size = wsme.wsattr(wtypes.text, mandatory=True)
    size = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, size='', virtual_size='', checksum=''):
        """init

        :param size:
        :param virtual_size:
        :param checksum:
        """
        self.checksum = checksum
        self.virtual_size = virtual_size
        self.size = size


class OutputResource(wtypes.DynamicBase):
    """class method returned json body."""

    region = wsme.wsattr(wtypes.text, mandatory=True)
    timestamp = wsme.wsattr(wtypes.text, mandatory=True)
    ord_transaction_id = wsme.wsattr(wtypes.text, mandatory=True)
    resource_id = wsme.wsattr(wtypes.text, mandatory=True)
    ord_notifier_id = wsme.wsattr(wtypes.text, mandatory=True)
    status = wsme.wsattr(wtypes.text, mandatory=True)
    error_code = wsme.wsattr(wtypes.text, mandatory=True)
    error_msg = wsme.wsattr(wtypes.text, mandatory=True)
    resource_extra_metadata = wsme.wsattr(ResourceMetaData, mandatory=False)
    operation = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, region="", timestamp="", ord_transaction_id="",
                 resource_id="", ord_notifier_id="", status="",
                 error_code="", error_msg="", operation="",
                 resource_meta_data=ResourceMetaData()):
        """init function.

        :param region: targets : list of lcp's
        :param timestamp:
        :param ord_transaction_id:
        :param resource_id:
        :param ord_notifier_id:
        :param status: success, error, submitted
        :param error_code:
        :param error_msg: error message
        """
        self.region = region
        self.timestamp = timestamp
        self.ord_notifier_id = ord_notifier_id
        self.ord_transaction_id = ord_transaction_id
        self.resource_id = resource_id
        self.status = status
        self.error_code = error_code
        self.error_msg = error_msg
        self.operation = operation
        if resource_meta_data:
            self.resource_extra_metadata = resource_meta_data


class Result(wtypes.DynamicBase):
    """class method json headers."""

    regions = wsme.wsattr([OutputResource], mandatory=True)
    status = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, status=[OutputResource()]):
        """init dunction.

        :param status: mian status: success, error, submitted
        """
        self.status = status    # pragma: no cover


class GetResource(rest.RestController):
    """controller get resource."""

    @wsexpose(Result, str, status_code=200, rest_content_types='json')
    def get(self, id):
        """get method.

        :param id: resource id
        :return: json output by resource id
        if no data for this resource id 404 will be returned
        :description: the function will get resource id check the DB for
        all resource status and return list of json data
        """
        logger.info("get status")
        logger.debug("get status data by resource id : %s" % id)
        result = regionResourceIdStatus.get_status_by_resource_id(id)

        if result is None or not result.regions:
            logger.error("no content for id %s " % id)
            raise EntityNotFoundError("resourceid %s" % id)
        logger.debug("items number : %s" % len(result.status))
        return result
