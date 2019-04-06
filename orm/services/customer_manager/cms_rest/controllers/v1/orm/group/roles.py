from oslo_db.exception import DBDuplicateEntry
from pecan import request, rest
from wsmeext.pecan import wsexpose

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.logic.group_logic import GroupLogic
from orm.services.customer_manager.cms_rest.model.GroupModels import \
    RoleAssignment, RoleResultWrapper
from orm.services.customer_manager.cms_rest.utils import authentication

LOG = get_logger(__name__)


class RoleController(rest.RestController):

    @wsexpose([str], str, rest_content_types='json')
    def get(self, group_id):
        return ["This is groups role controller ", "group id: " + group_id]

    @wsexpose(RoleResultWrapper, str, body=[RoleAssignment],
              rest_content_types='json', status_code=200)
    def post(self, group_id, role_assignments):
        LOG.info("RoleController - Assign Roles to group id {0} "
                 "roles: {1}".format(group_id, str(role_assignments)))
        authentication.authorize(request, 'groups:assign_region')
        try:
            group_logic = GroupLogic()
            result = group_logic.assign_roles(group_id,
                                              role_assignments,
                                              request.transaction_id)
            LOG.info("RoleController - Roles assigned: " + str(result))

            event_details = 'Group {} - roles assigned.'.format(group_id)
            utils.audit_trail('assigned group roles',
                              request.transaction_id,
                              request.headers,
                              group_id,
                              event_details=event_details)

        except DBDuplicateEntry as exception:
            LOG.log_exception(
                "RoleController - Group roles already exists", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=409,
                                      message='Roles already exists',
                                      error_details=exception.message)

        except ErrorStatus as exception:
            LOG.log_exception(
                "RoleController - Failed to assign roles", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception(
                "RoleController - Failed in assign roles", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(None, str, body=[RoleAssignment],
              rest_content_types='json', status_code=204)
    def delete(self, group_id, role_assignments):

        requester = request.headers.get('X-RANGER-Requester')
        is_rds_client_request = requester == 'rds_resource_service_proxy'
        LOG.info("Unassign Roles from group id {0} by RDS Proxy:"
                 " {1} ".format(group_id, is_rds_client_request))
        authentication.authorize(request, 'groups:unassign_region')
        try:
            group_logic = GroupLogic()
            group_logic.unassign_roles(group_id,
                                       role_assignments,
                                       request.transaction_id,
                                       is_rds_client_request)

            LOG.info("RoleController - Unassign Roles finished")

            event_details = 'Group {} roles unassigned'.format(group_id)
            utils.audit_trail('unassign group roles',
                              request.transaction_id,
                              request.headers,
                              group_id,
                              event_details=event_details)

        except ValueError as exception:
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)
        except ErrorStatus as exception:
            LOG.log_exception("RoleController - Failed to unassign roles",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("RoleController - Failed in unassign roles",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
