from pecan import rest, request, response
import oslo_db
from wsmeext.pecan import wsexpose

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer.regions import RegionController
from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer.users import DefaultUserController
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.group_logic import GroupLogic
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model.Models import Customer, CustomerResultWrapper, CustomerSummaryResponse
from orm.services.customer_manager.cms_rest.model.GroupModels import Group, GroupResultWrapper, GroupSummaryResponse
from orm.services.customer_manager.cms_rest.utils import authentication

LOG = get_logger(__name__)


class GroupController(rest.RestController):
    regions = RegionController()
    users = DefaultUserController()

    @wsexpose(Group, str, rest_content_types='json')
    def get(self, group_uuid):
        LOG.info("GroupController - GetGroupDetails: uuid is " + group_uuid)
        authentication.authorize(request, 'groups:get_one')
        try:
            group_logic = GroupLogic()
            result = group_logic.get_group(group_uuid)
            LOG.info("GroupController - GetGroupDetails finished well: " + str(result))

        except ErrorStatus as exception:
            LOG.log_exception("GroupController - Failed to GetGroupDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("GroupController - Failed to GetGroupDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)
        return result

    @wsexpose(GroupResultWrapper, body=Group, rest_content_types='json', status_code=201)
    def post(self, group):
        LOG.info("GroupController - CreateGroup: " + str(group))
        authentication.authorize(request, 'groups:create')
        try:
            uuid = None
            if not group.uuid:
                group.uuid = None
            group_logic = GroupLogic()       

            try:
                uuid = utils.create_or_validate_uuid(group.uuid, 'groupId')
            except TypeError:
                raise ErrorStatus(409.1, 'Unable to create Group ID {0}'.format(group.uuid))

            try:
                result = group_logic.create_group(group, uuid, request.transaction_id)
            except oslo_db.exception.DBDuplicateEntry as exception:
                raise ErrorStatus(409.2, 'Group field {0} already exists'.format(exception.columns))

            LOG.info("GroupController - Group Created: " + str(result))
            utils.audit_trail('create group', request.transaction_id,
                              request.headers, uuid,
                              event_details='')
            return result

        except ErrorStatus as exception:
            LOG.log_exception("GroupController - Failed to CreateGroup", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

    @wsexpose(GroupResultWrapper, str, body=Group, rest_content_types='json', status_code=200)
    def put(self, group_id, group):
        LOG.info("GroupController - UpdateGroup: " + str(group))
        authentication.authorize(request, 'groups:update')
        try:
            group_logic = GroupLogic()
            result = group_logic.update_group(group, group_id, request.transaction_id)
            response.status = 200
            LOG.info("GroupController - UpdateGroup finished well: " + str(group))

            utils.audit_trail('update group', request.transaction_id,
                              request.headers, group_id,
                              event_details='')

        except ErrorStatus as exception:
            LOG.log_exception("Failed in UpdateGroup", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("GroupController - Failed to UpdateGroup", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

        return result

    @wsexpose(GroupSummaryResponse, str, str, str, str, int, int,
              rest_content_types='json')
    def get_all(self, region=None, user=None, starts_with=None,
                contains=None, start=0, limit=0):
        LOG.info("GroupController - GetGrouplist")
        authentication.authorize(request, 'groups:get_all')

        # This shouldn't be necessary, but apparently is on mtn29
        start = 0 if start is None else start
        limit = 0 if limit is None else limit

        try:
            group_logic = GroupLogic()
            result = group_logic.get_group_list_by_criteria(region, user,
                                                                  starts_with,
                                                                  contains,
                                                                  start,
                                                                  limit)
            return result
        except ErrorStatus as exception:
            LOG.log_exception("GroupController - Failed to GetGrouplist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("GroupController - Failed to GetGrouplist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(None, str, rest_content_types='json', status_code=204)
    def delete(self, group_id):
        authentication.authorize(request, 'groups:delete')
        group_logic = GroupLogic()

        try:
            LOG.info("GroupController - DeleteGroup: uuid is " + group_id)
            group_logic.delete_group_by_uuid(group_id)
            LOG.info("GroupController - DeleteGroup finished well")

            event_details = 'Group {} deleted'.format(group_id)
            utils.audit_trail('delete group', request.transaction_id,
                              request.headers, group_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("GroupController - Failed to DeleteGroup",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("GroupController - Failed to DeleteGroup",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)
