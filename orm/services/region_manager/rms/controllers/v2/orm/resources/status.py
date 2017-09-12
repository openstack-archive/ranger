import logging

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.region_manager.rms.services import error_base
from orm.services.region_manager.rms.services import services as RegionService
from orm.services.region_manager.rms.utils import authentication

import pecan
from pecan import conf, request, rest
import wsme
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

logger = logging.getLogger(__name__)


class RegionStatus(wtypes.DynamicBase):
    """main json header."""

    status = wsme.wsattr(str, mandatory=True)
    links = wsme.wsattr({str: str}, mandatory=False)

    def __init__(self, status=None, links=None):
        """RegionStatus wrapper
        :param status:
        """
        self.status = status
        self.links = links


class RegionStatusController(rest.RestController):

    @wsexpose(RegionStatus, str, body=RegionStatus, status_code=201,
              rest_content_types='json')
    def put(self, region_id, new_status):
        """Handle put request to modify region status
        :param region_id:
        :param new_status:
        :return: 200 for updated, 404 for region not found
        400 invalid status
        """
        logger.info("Entered update region status")
        logger.debug("Got status: {}".format(new_status.status))

        authentication.authorize(request, 'status:put')

        try:
            allowed_status = conf.region_options.allowed_status_values[:]

            if new_status.status not in allowed_status:
                logger.error("Invalid status. Region status "
                             "must be one of {}".format(allowed_status))
                raise error_base.InputValueError(
                    message="Invalid status. Region status "
                            "must be one of {}".format(allowed_status))

            # May raise an exception which will return status code 400
            status = RegionService.update_region_status(region_id, new_status.status)
            base_link = 'https://{0}:{1}{2}'.format(conf.server.host, conf.server.port,
                                                    pecan.request.path)
            link = {'self': base_link}

            logger.debug("Region status for region id {}, was successfully "
                         "changed to: {}.".format(region_id, new_status.status))

            event_details = 'Region {} status updated to {}'.format(
                region_id, new_status.status)
            utils.audit_trail('Update status', request.transaction_id,
                              request.headers, region_id,
                              event_details=event_details)

            return RegionStatus(status, link)

        except error_base.ErrorStatus as e:
            logger.error(e.message)
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=e.status_code)
        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(str, str, rest_content_types='json')
    def get(self, region_id):
        raise err_utils.get_error(request.transaction_id,
                                  status_code=405)

    @wsexpose(RegionStatus, str, body=RegionStatus, status_code=200,
              rest_content_types='json')
    def post(self, region_id, status):
        raise err_utils.get_error(request.transaction_id,
                                  status_code=405)

    @wsexpose(str, str, rest_content_types='json')
    def delete(self, region_id):
        raise err_utils.get_error(request.transaction_id,
                                  status_code=405)
