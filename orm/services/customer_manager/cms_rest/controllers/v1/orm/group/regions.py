from oslo_db.exception import DBDuplicateEntry
from pecan import request, rest
from wsmeext.pecan import wsexpose

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.logic.group_logic import GroupLogic
from orm.services.customer_manager.cms_rest.model.GroupModels import \
    Region, RegionResultWrapper
from orm.services.customer_manager.cms_rest.utils import authentication

LOG = get_logger(__name__)


class RegionController(rest.RestController):

    @wsexpose([str], str, str, rest_content_types='json')
    def get(self, group_id, region_id):
        return ["This is groups region controller ", "group id: " + group_id]

    @wsexpose(RegionResultWrapper, str, body=[Region],
              rest_content_types='json', status_code=200)
    def post(self, group_id, regions):
        LOG.info("RegionController - Add Regions group id {0} "
                 "regions: {1}".format(group_id, str(regions)))
        authentication.authorize(request, 'groups:add_region')
        try:
            group_logic = GroupLogic()
            result = group_logic.add_regions(group_id,
                                             regions,
                                             request.transaction_id)
            LOG.info("RegionController - Add Regions finished: " + str(result))

            event_details = 'Group {} regions: {} added'.format(
                group_id, [r.name for r in regions])
            utils.audit_trail('add group regions',
                              request.transaction_id,
                              request.headers,
                              group_id,
                              event_details=event_details)

        except DBDuplicateEntry as exception:
            LOG.log_exception(
                "RegionController - Group Region already exists", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=409,
                                      message='Region already exists',
                                      error_details=exception.message)

        except ErrorStatus as exception:
            LOG.log_exception(
                "RegionController - Failed to add regions", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception(
                "RegionController - Failed in add regions", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(None, str, str, str, str, status_code=204)
    def delete(self, group_id, region_id, force_delete='False'):

        if force_delete == 'True':
            force_delete = True
        else:
            force_delete = False

        requester = request.headers.get('X-RANGER-Requester')
        is_rds_client_request = requester == 'rds_resource_service_proxy'
        LOG.info("Delete Region group id {0} region_id: {1} by RDS Proxy: "
                 " {2} ".format(group_id, region_id, is_rds_client_request))
        authentication.authorize(request, 'groups:delete_region')
        try:
            group_logic = GroupLogic()
            group_logic.delete_region(group_id,
                                      region_id,
                                      request.transaction_id,
                                      is_rds_client_request,
                                      force_delete)
            LOG.info("RegionController - Delete Region finished")

            event_details = 'Group {} region: {} deleted'.format(group_id,
                                                                 region_id)
            utils.audit_trail('delete group region',
                              request.transaction_id,
                              request.headers,
                              group_id,
                              event_details=event_details)

        except ValueError as exception:
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)
        except ErrorStatus as exception:
            LOG.log_exception("RegionController - Failed to delete region",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("RegionController - Failed in delete Region",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
