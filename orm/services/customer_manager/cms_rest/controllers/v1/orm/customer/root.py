from pecan import rest, request, response
import oslo_db
from wsmeext.pecan import wsexpose

from cms_rest.controllers.v1.orm.customer.enabled import EnabledController
from cms_rest.controllers.v1.orm.customer.metadata import MetadataController
from cms_rest.controllers.v1.orm.customer.regions import RegionController
from cms_rest.controllers.v1.orm.customer.users import DefaultUserController
from cms_rest.logic.customer_logic import CustomerLogic
from cms_rest.logic.error_base import ErrorStatus
from cms_rest.model.Models import Customer, CustomerResultWrapper, CustomerSummaryResponse
from cms_rest.utils import authentication
from orm_common.utils import api_error_utils as err_utils
from orm_common.utils import utils

from cms_rest.logger import get_logger

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
            if not customer.custId:
                uuid = utils.make_uuid()
            else:
                if not CustomerController.validate_cust_id(customer.custId):
                    utils.audit_trail('create customer', request.transaction_id, request.headers, customer.custId)
                    raise ErrorStatus('400', None)
                try:
                    uuid = utils.create_existing_uuid(customer.custId)
                except TypeError:
                    raise ErrorStatus(409.1, 'Customer ID {0} already exists'.format(customer.custId))

            customer_logic = CustomerLogic()
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

    @wsexpose(CustomerSummaryResponse, str, str, str, str, [str],
              rest_content_types='json')
    def get_all(self, region=None, user=None, starts_with=None,
                contains=None, metadata=None):
        LOG.info("CustomerController - GetCustomerlist")
        authentication.authorize(request, 'customers:get_all')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.get_customer_list_by_criteria(region, user,
                                                                  starts_with,
                                                                  contains,
                                                                  metadata)

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

    @staticmethod
    def validate_cust_id(cust_id):
        # regex = re.compile('[a-zA-Z]')
        # return regex.match(cust_id[0])
        return True
