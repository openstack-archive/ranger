import logging

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.services.region_manager.rms.model import url_parm
from orm.services.region_manager.rms.services.error_base import ErrorStatus
from orm.services.region_manager.rms.services import services
from orm.services.region_manager.rms.utils import authentication

from pecan import request, rest
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

logger = logging.getLogger(__name__)


class LcpController(rest.RestController):

    @wsexpose(wtypes.text, rest_content_types='json')
    def get_all(self):
        """This function is called when receiving /lcp without a parameter.
            parameter:
                None.
            return: entire list of lcp.
        """
        logger.info('Received a GET request for all LCPs')
        authentication.authorize(request, 'lcp:get_all')

        zones = []

        try:
            zones = get_zones()
            logger.debug('Returning LCP list: %s' % (zones,))
            return zones

        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(wtypes.text, str, rest_content_types='json')
    def get_one(self, lcp_id):

        logger.info('Received a GET request for LCP %s' % (id,))
        authentication.authorize(request, 'lcp:get_one')

        zones = []
        try:

            zones = get_zones()

        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

        for zone in zones:
            if zone["id"] == lcp_id:
                logger.debug('Returning: %s' % (zone,))
                return zone

        error_msg = 'LCP %s not found' % (lcp_id,)
        logger.info(error_msg)
        raise err_utils.get_error(request.transaction_id,
                                  message=error_msg,
                                  status_code=404)


def get_zones():
    """This function returns the lcp list from CSV file.

    parameter:
        None.
    return:
        zone list in json format.
    """
    logger.debug('Enter get_zones function')
    result = []

    try:
        url_args = url_parm.UrlParms()
        zones = services.get_regions_data(url_args)

        for zone in zones.regions:
            result.append(build_zone_response(zone))

        logger.debug("Available regions: {}".format(', '.join(
            [region["zone_name"] for region in result])))

    except ErrorStatus as e:
        logger.debug(e.message)
    finally:
        return result


def build_zone_response(zone):

    end_points_dict = {"identity": "",
                       "dashboard": "",
                       "ord": ""}
    for end_point in zone.endpoints:
        end_points_dict[end_point.type] = end_point.publicurl

    return dict(
        zone_name=zone.name,
        id=zone.id,
        status="1" if zone.status == "functional" else "0",
        design_type=zone.design_type,
        location_type=zone.location_type,
        vLCP_name=zone.vlcp_name,
        AIC_version=zone.ranger_agent_version,
        OS_version=zone.open_stack_version,
        keystone_EP=end_points_dict["identity"],
        horizon_EP=end_points_dict["dashboard"],
        ORD_EP=end_points_dict["ord"]
    )
