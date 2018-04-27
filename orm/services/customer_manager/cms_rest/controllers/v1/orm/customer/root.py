from pecan import rest, request, response
import oslo_db
from wsmeext.pecan import wsexpose

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer.enabled import EnabledController
from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer.metadata import MetadataController
from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer.regions import RegionController
from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer.users import DefaultUserController
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.customer_logic import CustomerLogic
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model.Models import Customer, CustomerResultWrapper, CustomerSummaryResponse
from orm.services.customer_manager.cms_rest.utils import authentication

LOG = get_logger(__name__)


class CustomerController(rest.RestController):
    regions = RegionController()
    users = DefaultUserController()
    metadata = MetadataController()
    enabled = EnabledController()

    @wsexpose(Customer, str, rest_content_types='json')
    def get(self, customer_uuid):
        LOG.info("CustomerController - GetCustomerDetails: uuid is " + customer_uuid)
        authentication.authorize(request, 'customers:get_one')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.get_customer(customer_uuid)
            LOG.info("CustomerController - GetCustomerDetails finished well: " + str(result))

        except ErrorStatus as exception:
            LOG.log_exception("CustomerController - Failed to GetCustomerDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("CustomerController - Failed to GetCustomerDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

        return result

    @wsexpose(CustomerResultWrapper, body=Customer, rest_content_types='json', status_code=201)
    def post(self, customer):
        LOG.info("CustomerController - CreateCustomer: " + str(customer))
        authentication.authorize(request, 'customers:create')
        try:
            uuid = None
            if not customer.uuid:
                customer.uuid = None
            customer_logic = CustomerLogic()

            try:
                uuid = utils.create_or_validate_uuid(customer.uuid, 'custId')
            except TypeError:
                raise ErrorStatus(409.1, 'Unable to create Customer ID {0}'.format(customer.uuid))

            try:
                result = customer_logic.create_customer(customer, uuid, request.transaction_id)
            except oslo_db.exception.DBDuplicateEntry as exception:
                raise ErrorStatus(409.2, 'Customer field {0} already exists'.format(exception.columns))

            LOG.info("CustomerController - Customer Created: " + str(result))
            event_details = 'Customer {} {} created in regions: {}, with users: {}'.format(
                uuid, customer.name, [r.name for r in customer.regions],
                [u.id for u in customer.users])
            utils.audit_trail('create customer', request.transaction_id,
                              request.headers, uuid,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("CustomerController - Failed to CreateCustomer", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("CustomerController - Failed to CreateCustomer", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(CustomerResultWrapper, str, body=Customer, rest_content_types='json', status_code=200)
    def put(self, customer_id, customer):
        LOG.info("CustomerController - UpdateCustomer: " + str(customer))
        authentication.authorize(request, 'customers:update')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.update_customer(customer, customer_id, request.transaction_id)
            response.status = 200
            LOG.info("CustomerController - UpdateCustomer finished well: " + str(customer))

            event_details = 'Customer {} {} updated in regions: {}, with users: {}'.format(
                customer_id, customer.name, [r.name for r in customer.regions],
                [u.id for u in customer.users])
            utils.audit_trail('update customer', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("Failed in UpdateCustomer", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("CustomerController - Failed to UpdateCustomer", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

        return result

    @wsexpose(CustomerSummaryResponse, str, str, str, str, [str], int, int,
              rest_content_types='json')
    def get_all(self, region=None, user=None, starts_with=None,
                contains=None, metadata=None, start=0, limit=0):
        LOG.info("CustomerController - GetCustomerlist")
        authentication.authorize(request, 'customers:get_all')

        # This shouldn't be necessary, but apparently is on mtn29
        start = 0 if start is None else start
        limit = 0 if limit is None else limit

        try:
            customer_logic = CustomerLogic()
            result = customer_logic.get_customer_list_by_criteria(region, user,
                                                                  starts_with,
                                                                  contains,
                                                                  metadata,
                                                                  start,
                                                                  limit)
            return result
        except ErrorStatus as exception:
            LOG.log_exception("CustomerController - Failed to GetCustomerlist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("CustomerController - Failed to GetCustomerlist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(None, str, rest_content_types='json', status_code=204)
    def delete(self, customer_id):
        authentication.authorize(request, 'customers:delete')
        customer_logic = CustomerLogic()

        try:
            LOG.info("CustomerController - DeleteCustomer: uuid is " + customer_id)
            customer_logic.delete_customer_by_uuid(customer_id)
            LOG.info("CustomerController - DeleteCustomer finished well")

            event_details = 'Customer {} deleted'.format(customer_id)
            utils.audit_trail('delete customer', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("CustomerController - Failed to DeleteCustomer",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("CustomerController - Failed to DeleteCustomer",
                              exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)
