from oslo_db.exception import DBDuplicateEntry
from pecan import request, rest
from wsmeext.pecan import wsexpose

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.controllers.v1.orm.customer.users import UserController
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.customer_logic import CustomerLogic
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model.Models import Region, RegionResultWrapper
from orm.services.customer_manager.cms_rest.utils import authentication

LOG = get_logger(__name__)


class RegionController(rest.RestController):

    users = UserController()

    @wsexpose([str], str, str, rest_content_types='json')
    def get(self, customer_id, region_id):
        return ["This is the regions controller ", "customer id: " + customer_id]

    @wsexpose(RegionResultWrapper, str, body=[Region], rest_content_types='json', status_code=200)
    def post(self, customer_id, regions):
        LOG.info("RegionController - Add Regions (post) customer id {0} regions: {1}".format(customer_id, str(regions)))
        authentication.authorize(request, 'customers:add_region')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.add_regions(customer_id, regions, request.transaction_id)
            LOG.info("RegionController - Add Regions (post) finished well: " + str(result))

            event_details = 'Customer {} regions: {} added'.format(
                customer_id, [r.name for r in regions])
            utils.audit_trail('add regions', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except DBDuplicateEntry as exception:
            LOG.log_exception("RegionController - Add Regions (post) - region already exists", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=409,
                                      message='Region already exists',
                                      error_details=exception.message)

        except ErrorStatus as exception:
            LOG.log_exception("CustomerController - Failed to update regions", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("RegionController - Add Regions (post) - Failed to update regions", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(RegionResultWrapper, str, body=[Region], rest_content_types='json', status_code=200)
    def put(self, customer_id, regions):
        LOG.info("RegionController - Replace Regions (put) customer id {0} regions: {1}".format(customer_id, str(regions)))
        authentication.authorize(request, 'customers:update_region')
        self.validate_put_url()
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.replace_regions(customer_id, regions, request.transaction_id)
            LOG.info("RegionController - Replace Regions (put) finished well: " + str(result))

            event_details = 'Customer {} regions: {} updated'.format(
                customer_id, [r.name for r in regions])
            utils.audit_trail('Replace regions', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("CustomerController - Failed to Replace regions", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("RegionController - Replace Regions (put) - Failed to replace regions", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(None, str, str, str, status_code=204)
    def delete(self, customer_id, region_id, force_delete='False'):

        if force_delete == 'True':
            force_delete = True
        else:
            force_delete = False
        requester = request.headers.get('X-AIC-ORM-Requester')
        is_rds_client_request = requester == 'rds_resource_service_proxy'
        LOG.info("Delete Region (delete) customer id {0} region_id: {1} by RDS Proxy: {2} ".format(customer_id, region_id, is_rds_client_request))
        authentication.authorize(request, 'customers:delete_region')
        try:
            customer_logic = CustomerLogic()
            customer_logic.delete_region(customer_id, region_id, request.transaction_id)
            LOG.info("RegionController - Delete Region (delete) finished well")

            event_details = 'Customer {} region: {} deleted'.format(
                customer_id, region_id)
            utils.audit_trail('delete region', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except ValueError as exception:
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)
        except ErrorStatus as exception:
            LOG.log_exception("CustomerController - Failed to delete region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("RegionController - Failed in delete Region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @staticmethod
    def validate_put_url():
        url_elements = request.path.split('/')
        last_index = -2 if url_elements[-1] == '' else -1
        # If there's an element after 'regions', it is a region ID
        # which is currently unsupported
        if url_elements[last_index - 1] == 'regions':
            LOG.debug('Method not allowed for a specific region in Request: {}'.format(request.path))
            raise err_utils.get_error(request.transaction_id,
                                      message='Method not allowed for a specific region',
                                      status_code=405)
