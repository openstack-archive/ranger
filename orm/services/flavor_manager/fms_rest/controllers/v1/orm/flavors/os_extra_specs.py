from __future__ import absolute_import

from orm.common.orm_common.injector import injector
from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.services.flavor_manager.fms_rest.data.wsme.models import ExtraSpecsWrapper
from orm.services.flavor_manager.fms_rest.logger import get_logger
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus
from orm.services.flavor_manager.fms_rest.utils import authentication

from pecan import request, rest
from wsmeext.pecan import wsexpose

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('flavor_logic')
@di.dependsOn('utils')
class OsExtraSpecsController(rest.RestController):
    """main class."""

    def _extra_specs_redefined(self, extra_specs_wrapper):
        # make sure at least one exit and not both at same time
        valid_json = not extra_specs_wrapper.extra_specs and not \
            extra_specs_wrapper.os_extra_specs or \
            extra_specs_wrapper.os_extra_specs and\
            extra_specs_wrapper.extra_specs
        if valid_json:
            raise ErrorStatus(message="Invalid json. please provide supported json",
                              status_code=400)
        if extra_specs_wrapper.extra_specs:
            extra_specs_wrapper.os_extra_specs = extra_specs_wrapper.extra_specs

        return extra_specs_wrapper

    @wsexpose(ExtraSpecsWrapper, str, rest_content_types='json',
              status_code=200)
    def get(self, flavor_id):
        flavor_logic, utils = di.resolver.unpack(OsExtraSpecsController)

        LOG.info(
            "OsExtraSpecsController - get all extra specs for flavor: {} ".format(
                flavor_id))
        authentication.authorize(request, 'flavor:get_flavor_extra_specs')

        try:
            result = flavor_logic.get_extra_specs_uuid(flavor_id,
                                                       request.transaction_id)
            LOG.info("OsExtraSpecsController - GOT extra specs: {} ".format(result))
            utils.audit_trail("get extra specs", request.transaction_id,
                              request.headers, flavor_id)
            return result

        except ErrorStatus as exception:
            LOG.log_exception(
                "OsExtraSpecsController - Failed to get extra specs", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception(
                "OsExtraSpecsController - Failed to get extra specs", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(ExtraSpecsWrapper, str, body=ExtraSpecsWrapper, rest_content_types='json', status_code=201)
    def post(self, flavor_id, extra_specs_wrapper):
        flavor_logic, utils = di.resolver.unpack(OsExtraSpecsController)
        LOG.info("OsExtraSpecsController - add extra specs: " + str(
            extra_specs_wrapper.os_extra_specs))
        authentication.authorize(request, 'flavor:add_flavor_extra_specs')

        try:
            # for backward_compatibility
            extra_specs_wrapper = self._extra_specs_redefined(
                extra_specs_wrapper)

            result = flavor_logic.add_extra_specs(flavor_id,
                                                  extra_specs_wrapper,
                                                  request.transaction_id)
            LOG.info("OsExtraSpecsController - extra specs added ")
            utils.audit_trail('add extra specs', request.transaction_id,
                              request.headers, flavor_id)
            return result

        except ErrorStatus as exception:
            LOG.log_exception(
                "OsExtraSpecsController - Failed to add extra specs", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception(
                "OsExtraSpecsController - Failed to add extra specs", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, str, rest_content_types='json', status_code=204)
    def delete(self, flavor_id, extra_spec=None):
        flavor_logic, utils = di.resolver.unpack(OsExtraSpecsController)
        LOG.info(
            "OsExtraSpecsController - delete flavor {} extra spec".format(
                flavor_id))
        authentication.authorize(request, 'flavor:delete_flavor_extra_specs')

        try:
            flavor_logic.delete_extra_specs(flavor_id, request.transaction_id,
                                            extra_spec)
            LOG.info(
                "OsExtraSpecsController - extra spec was deleted for  flavor {} c".format(
                    flavor_id))
            utils.audit_trail('delete extra spec', request.transaction_id,
                              request.headers, flavor_id)
            return

        except ErrorStatus as exception:
            LOG.log_exception(
                "OsExtraSpecsController - Failed to delete extra specs", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("OsExtraSpecsController - Failed to delete extra specs",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(ExtraSpecsWrapper, str, body=ExtraSpecsWrapper, rest_content_types='json',
              status_code=200)
    def put(self, flavor_id, extra_specs_wrapper):
        LOG.info("OsExtraSpecsController -  update extra specs of flavor {}".format(flavor_id))
        flavor_logic, utils = di.resolver.unpack(OsExtraSpecsController)
        LOG.info(
            "OsExtraSpecsController - update extra specs with {} ".format(
                extra_specs_wrapper.os_extra_specs))
        authentication.authorize(request, 'flavor:replace_flavor_extra_specs')

        try:
            # for backward_compatibility
            extra_specs_wrapper = self._extra_specs_redefined(
                extra_specs_wrapper)

            result = flavor_logic.update_extra_specs(flavor_id,
                                                     extra_specs_wrapper,
                                                     request.transaction_id)
            LOG.info("OsExtraSpecsController - extra specs updated")
            utils.audit_trail('update extra specs', request.transaction_id,
                              request.headers, flavor_id)
            return result

        except ErrorStatus as exception:
            LOG.log_exception(
                "OsExtraSpecsController - Failed to update extra specs", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception(
                "OsExtraSpecsController - Failed to update extra specs", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
