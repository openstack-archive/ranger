from fms_rest.data.wsme.models import TagsWrapper
from fms_rest.logger import get_logger
from fms_rest.logic.error_base import ErrorStatus
from fms_rest.utils import authentication
from orm_common.injector import injector
from orm_common.utils import api_error_utils as err_utils
from pecan import request, rest
from wsmeext.pecan import wsexpose

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('flavor_logic')
@di.dependsOn('utils')
class TagsController(rest.RestController):
    @wsexpose(TagsWrapper, str, body=TagsWrapper, rest_content_types='json', status_code=201)
    def post(self, flavor_id, tags_wrapper):
        flavor_logic, utils = di.resolver.unpack(TagsController)
        LOG.info("TagsController - add tags: " + str(
            tags_wrapper.tags))

        authentication.authorize(request, 'flavor:add_flavor_tags')

        try:
            result = flavor_logic.add_tags(flavor_id, tags_wrapper,
                                           request.transaction_id)

            LOG.info("TagsController - tags added")
            utils.audit_trail('add tags', request.transaction_id,
                              request.headers, flavor_id)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("TagsController - Failed to add tags", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("TagsController - Failed to add tags", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, str, rest_content_types='json', status_code=204)
    def delete(self, flavor_id, tag_to_delete=None):
        flavor_logic, utils = di.resolver.unpack(TagsController)
        LOG.info(
            "TagsController - delete flavor {} tags".format(
                flavor_id))
        authentication.authorize(request, 'flavor:delete_flavor_tags')

        try:
            flavor_logic.delete_tags(flavor_id, tag_to_delete,
                                     request.transaction_id)
            LOG.info(
                "TagsController - tags deleted for flavor {}".format(
                    flavor_id))
            utils.audit_trail('delete tags', request.transaction_id,
                              request.headers, flavor_id, 'Saved to DB')

        except ErrorStatus as exp:
            LOG.log_exception(
                "TagsController - Failed to delete tags", exp)
            utils.audit_trail('delete tags', request.transaction_id,
                              request.headers, flavor_id)
            raise err_utils.get_error(request.transaction_id,
                                      message=exp.message,
                                      status_code=exp.status_code)
        except Exception as exp:
            LOG.log_exception("TagsController - Failed to delete tags",
                              exp)
            utils.audit_trail('delete tags', request.transaction_id,
                              request.headers, flavor_id)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exp))

        return

    @wsexpose(TagsWrapper, str, body=TagsWrapper, rest_content_types='json',
              status_code=200)
    def put(self, flavor_id, tags_wrapper):
        LOG.info("TagsController - update tags of flavor {}".format(flavor_id))
        flavor_logic, utils = di.resolver.unpack(TagsController)
        LOG.info("TagsController - update tags with {} ".format(tags_wrapper.tags))
        authentication.authorize(request, 'flavor:replace_flavor_tags')

        try:
            result = flavor_logic.update_tags(flavor_id, tags_wrapper, request.transaction_id)
            LOG.info("TagsController - tags updated")
            utils.audit_trail('update tags', request.transaction_id, request.headers, flavor_id)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("TagsController - Failed to update tags", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("TagsController - Failed to update tags", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(TagsWrapper, str, rest_content_types='json', status_code=200)
    def get(self, flavor_id):
        flavor_logic, utils = di.resolver.unpack(TagsController)
        LOG.info("TagsController - get tags of flavor {}".format(flavor_id))
        authentication.authorize(request, 'flavor:get_flavor_tags')

        try:
            result = flavor_logic.get_tags(flavor_id)
            LOG.debug("TagsController - got tags successfully")
            utils.audit_trail('get tags', request.transaction_id,
                              request.headers, flavor_id)
            return TagsWrapper(result)

        except ErrorStatus as exception:
            LOG.log_exception(
                "TagsController - Failed to get tags", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception(
                "TagsController - Failed to get tags", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
