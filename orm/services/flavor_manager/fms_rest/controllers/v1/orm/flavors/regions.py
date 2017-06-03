from pecan import rest, request
from wsmeext.pecan import wsexpose

from fms_rest.data.wsme.models import RegionWrapper
from fms_rest.logic.error_base import ErrorStatus
from base import ClientSideError
from fms_rest.logger import get_logger

from orm_common.injector import injector
from orm_common.utils import api_error_utils as err_utils
from fms_rest.utils import authentication

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('flavor_logic')
@di.dependsOn('utils')
class RegionController(rest.RestController):
    @wsexpose(RegionWrapper, str, body=RegionWrapper, rest_content_types='json', status_code=201)
    def post(self, flavor_id, region_wrapper):
        flavor_logic, utils = di.resolver.unpack(RegionController)

        LOG.info("RegionController - add regions: " + str(region_wrapper))
        authentication.authorize(request, 'flavor:add_flavor_regions')

        try:
            result = flavor_logic.add_regions(flavor_id, region_wrapper, request.transaction_id)

            LOG.info("RegionController - regions added: " + str(result))

            event_details = 'Flavor {} regions: {} added'.format(
                flavor_id, [r.name for r in region_wrapper.regions])
            utils.audit_trail('add regions', request.transaction_id,
                              request.headers, flavor_id,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("RegionController - Failed to add region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("RegionController - Failed to add region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, str, rest_content_types='json', status_code=204)
    def delete(self, flavor_id, region_name):
        flavor_logic, utils = di.resolver.unpack(RegionController)

        LOG.info("RegionController - delete region: " + str(region_name))
        authentication.authorize(request, 'flavor:delete_flavor_region')

        try:
            result = flavor_logic.delete_region(flavor_id, region_name, request.transaction_id)

            LOG.info("RegionController - region deleted: " + str(result))

            event_details = 'Flavor {} region {} deleted'.format(flavor_id,
                                                                 region_name)
            utils.audit_trail('delete region', request.transaction_id,
                              request.headers, flavor_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("RegionController - Failed to delete region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("RegionController - Failed to delete region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
