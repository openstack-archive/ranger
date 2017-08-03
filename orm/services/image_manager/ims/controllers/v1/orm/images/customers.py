from ims.logger import get_logger
from ims.logic.error_base import ErrorStatus
from ims.persistency.wsme.models import CustomerWrapper, ImageWrapper
from ims.utils import authentication as auth
from orm_common.injector import injector
from orm_common.utils import api_error_utils as err_utils
from pecan import request, rest
from wsmeext.pecan import wsexpose

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('image_logic')
@di.dependsOn('utils')
class CustomerController(rest.RestController):

    @wsexpose(ImageWrapper, str, body=CustomerWrapper, rest_content_types='json', status_code=201)
    def post(self, image_id, cust_wrapper):
        image_logic, utils = di.resolver.unpack(CustomerController)
        auth.authorize(request, "tenant:create")
        try:
            LOG.info("CustomerController - add tenants: " + str(cust_wrapper))

            result = image_logic.add_customers(image_id, cust_wrapper, request.transaction_id)

            LOG.info("CustomerController - tenants added: " + str(result))

            event_details = 'Image {} tenants: {} added'.format(
                image_id, cust_wrapper.customers)
            utils.audit_trail('add tenants', request.transaction_id,
                              request.headers, image_id,
                              event_details=event_details)
            return result

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

    @wsexpose(ImageWrapper, str, body=CustomerWrapper, rest_content_types='json', status_code=200)
    def put(self, image_id, cust_wrapper):
        image_logic, utils = di.resolver.unpack(CustomerController)
        auth.authorize(request, "tenant:update")
        try:
            LOG.info("CustomerController - replace tenants: " + str(cust_wrapper))

            result = image_logic.replace_customers(image_id, cust_wrapper, request.transaction_id)

            LOG.info("CustomerController - tenants replaced: " + str(result))

            event_details = 'Image {} tenants: {} updated'.format(
                image_id, cust_wrapper.customers)
            utils.audit_trail('replace tenants', request.transaction_id,
                              request.headers, image_id,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("TenantController - Failed to replace tenants", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("TenantController - Failed to replace tenants", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, str, rest_content_types='json', status_code=204)
    def delete(self, image_id, cust_id):
        image_logic, utils = di.resolver.unpack(CustomerController)
        auth.authorize(request, "tenant:delete")

        try:
            LOG.info("TenantController - delete tenant: " + str(cust_id))

            result = image_logic.delete_customer(image_id, cust_id, request.transaction_id)

            LOG.info("TenantController - tenant deleted: " + str(result))

            event_details = 'Image {} tenant {} deleted'.format(
                image_id, cust_id)
            utils.audit_trail('delete tenant', request.transaction_id,
                              request.headers, image_id,
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
