from orm.common.orm_common.injector import injector
from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.flavor_manager.fms_rest.data.wsme.models import TenantWrapper
from orm.services.flavor_manager.fms_rest.logger import get_logger
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus
from orm.services.flavor_manager.fms_rest.utils import authentication

from pecan import request, rest
from wsmeext.pecan import wsexpose

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('flavor_logic')
class TenantController(rest.RestController):

    @wsexpose(TenantWrapper, str, body=TenantWrapper, rest_content_types='json', status_code=201)
    def post(self, flavor_id, tenant_wrapper):
        flavor_logic = di.resolver.unpack(TenantController)
        LOG.info("TenantController - add tenants: " + str(tenant_wrapper))
        authentication.authorize(request, 'flavor:add_flavor_tenants')

        try:
            result = flavor_logic.add_tenants(flavor_id, tenant_wrapper, request.transaction_id)

            LOG.info("TenantController - tenants added: " + str(result))

            event_details = 'Flavor {} tenants: {} added'.format(
                flavor_id, tenant_wrapper.tenants)
            utils.audit_trail('add tenants', request.transaction_id,
                              request.headers, flavor_id,
                              event_details=event_details)
            return result

        except ValueError as exception:
            LOG.log_exception("TenantController - Failed to add tenants", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=400)

        except ErrorStatus as exception:
            LOG.log_exception("TenantController - Failed to add tenants", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("TenantController - Failed to add tenants", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, str, rest_content_types='json', status_code=204)
    def delete(self, flavor_id, tenant_id):
        flavor_logic = di.resolver.unpack(TenantController)
        LOG.info("TenantController - delete tenant: " + str(tenant_id))
        authentication.authorize(request, 'flavor:delete_flavor_tenant')

        try:

            result = flavor_logic.delete_tenant(flavor_id, tenant_id, request.transaction_id)

            LOG.info("TenantController - tenant deleted: " + str(result))

            event_details = 'Flavor {} tenant {} deleted'.format(flavor_id,
                                                                 tenant_id)
            utils.audit_trail('delete tenant', request.transaction_id,
                              request.headers, flavor_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("TenantController - Failed to delete tenant", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("TenantController - Failed to delete tenant", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(str, str, rest_content_types='json')
    def get(self, flavor_id):
        LOG.error("Get tenants is not supported")
        raise err_utils.get_error(request.transaction_id,
                                  status_code=405)
