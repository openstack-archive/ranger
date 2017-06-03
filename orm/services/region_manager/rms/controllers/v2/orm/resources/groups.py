"""rest module."""
import logging
import time
import wsme

from orm_common.utils import api_error_utils as err_utils
from orm_common.utils import utils

from rms.services import error_base
from rms.services import services as GroupService
from rms.utils import authentication
from pecan import rest, request
from wsme import types as wtypes
from wsmeext.pecan import wsexpose
from rms.model import model as PythonModel


logger = logging.getLogger(__name__)


class Groups(wtypes.DynamicBase):
    """main json header."""

    id = wsme.wsattr(wtypes.text, mandatory=True)
    name = wsme.wsattr(wtypes.text, mandatory=True)
    description = wsme.wsattr(wtypes.text, mandatory=True)
    regions = wsme.wsattr([str], mandatory=True)

    def __init__(self, id=None, name=None, description=None, regions=[]):
        """init function.

        :param regions:
        :return:
        """
        self.id = id
        self.name = name
        self.description = description
        self.regions = regions

    def _to_python_obj(self):
        obj = PythonModel.Groups()
        obj.id = self.id
        obj.name = self.name
        obj.description = self.description
        obj.regions = self.regions
        return obj


class GroupWrapper(wtypes.DynamicBase):
    """main cotain lis of groups."""

    groups = wsme.wsattr([Groups], mandatory=True)

    def __init__(self, groups=[]):
        """

        :param group:
        """
        self.groups = groups


class OutputResource(wtypes.DynamicBase):
    """class method returned json body."""

    id = wsme.wsattr(wtypes.text, mandatory=True)
    name = wsme.wsattr(wtypes.text, mandatory=True)
    created = wsme.wsattr(wtypes.text, mandatory=True)
    links = wsme.wsattr({str: str}, mandatory=True)

    def __init__(self, id=None, name=None, created=None, links={}):
        """init function.

        :param id:
        :param created:
        :param links:
        """
        self.id = id
        self.name = name
        self.created = created
        self.links = links


class Result(wtypes.DynamicBase):
    """class method json headers."""

    group = wsme.wsattr(OutputResource, mandatory=True)

    def __init__(self, group=OutputResource()):
        """init dunction.

        :param group: The created group
        """
        self.group = group


class GroupsController(rest.RestController):
    """controller get resource."""

    @wsexpose(Groups, str, status_code=200,
              rest_content_types='json')
    def get(self, id=None):
        """Handle get request.

        :param id: Group ID
        :return: 200 OK on success, 404 Not Found otherwise.
        """
        logger.info("Entered Get Group: id = {}".format(id))
        authentication.authorize(request, 'group:get_one')

        try:

            result = GroupService.get_groups_data(id)
            logger.debug('Returning group, regions: {}'.format(result.regions))
            return result

        except error_base.NotFoundError as e:
            logger.error("GroupsController - Group not found")
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=404)
        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(GroupWrapper, status_code=200, rest_content_types='json')
    def get_all(self):
        logger.info("gett all groups")
        authentication.authorize(request, 'group:get_all')
        try:

            logger.debug("api-get all groups")
            groups_wrraper = GroupService.get_all_groups()
            logger.debug("got groups {}".format(groups_wrraper))

        except Exception as exp:
            logger.error("api--fail to get all groups")
            logger.exception(exp)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

        return groups_wrraper

    @wsexpose(Result, body=Groups, status_code=201, rest_content_types='json')
    def post(self, group_input):
        """Handle post request.

        :param group_input: json data
        :return: 201 created on success, 409 otherwise.
        """
        logger.info("Entered Create Group")
        logger.debug("id = {}, name = {}, description = {}, regions = {}".format(
            group_input.id,
            group_input.name,
            group_input.description,
            group_input.regions))
        authentication.authorize(request, 'group:create')

        try:
            # May raise an exception which will return status code 400
            GroupService.create_group_in_db(group_input.id,
                                            group_input.name,
                                            group_input.description,
                                            group_input.regions)
            logger.debug("Group created successfully in DB")

            # Create the group output data with the correct timestamp and link
            group = OutputResource(group_input.id,
                                   group_input.name,
                                   repr(int(time.time() * 1000)),
                                   {'self': '{}/v2/orm/groups/{}'.format(
                                       request.application_url,
                                       group_input.id)})

            event_details = 'Region group {} {} created with regions: {}'.format(
                group_input.id, group_input.name, group_input.regions)
            utils.audit_trail('create group', request.transaction_id,
                              request.headers, group_input.id,
                              event_details=event_details)
            return Result(group)

        except error_base.ErrorStatus as e:
            logger.error("GroupsController - {}".format(e.message))
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=e.status_code)
        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(None, str, status_code=204, rest_content_types='json')
    def delete(self, group_id):
        logger.info("delete group")
        authentication.authorize(request, 'group:delete')

        try:

            logger.debug("delete group with id {}".format(group_id))
            GroupService.delete_group(group_id)
            logger.debug("done")

            event_details = 'Region group {} deleted'.format(group_id)
            utils.audit_trail('delete group', request.transaction_id,
                              request.headers, group_id,
                              event_details=event_details)

        except Exception as exp:

            logger.exception("fail to delete group :- {}".format(exp))
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exp.message)
        return

    @wsexpose(Result, str, body=Groups, status_code=201,
              rest_content_types='json')
    def put(self, group_id, group):
        logger.info("update group")
        authentication.authorize(request, 'group:update')

        try:
            logger.debug("update group - id {}".format(group_id))
            result = GroupService.update_group(group, group_id)
            logger.debug("group updated to :- {}".format(result))

            # build result
            group_result = OutputResource(result.id, result.name,
                                          repr(int(time.time() * 1000)), {
                                              'self': '{}/v2/orm/groups/{}'.format(
                                                  request.application_url,
                                                  result.id)})

            event_details = 'Region group {} {} updated with regions: {}'.format(
                group_id, group.name, group.regions)
            utils.audit_trail('update group', request.transaction_id,
                              request.headers, group_id,
                              event_details=event_details)

        except error_base.ErrorStatus as exp:
            logger.error("group to update not found {}".format(exp))
            logger.exception(exp)
            raise err_utils.get_error(request.transaction_id,
                                      message=exp.message,
                                      status_code=exp.status_code)
        except Exception as exp:
            logger.error("fail to update groupt -- id {}".format(group_id))
            logger.exception(exp)
            raise

        return Result(group_result)
