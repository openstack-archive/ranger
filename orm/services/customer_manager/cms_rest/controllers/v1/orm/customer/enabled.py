from pecan import request, rest
from wsmeext.pecan import wsexpose

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.customer_logic import CustomerLogic
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model.Models import CustomerResultWrapper, Enabled
from orm.services.customer_manager.cms_rest.utils import authentication

LOG = get_logger(__name__)


class EnabledController(rest.RestController):
    @wsexpose(CustomerResultWrapper, str, body=Enabled, rest_content_types='json')
    def put(self, customer_uuid, enable):
        authentication.authorize(request, 'customers:enable')
        try:
            LOG.info("EnabledController - (put) customer id {0} enable: {1}".format(customer_uuid, enable))
            customer_logic = CustomerLogic()
            result = customer_logic.enable(customer_uuid, enable, request.transaction_id)
            LOG.info("EnabledController - change enable (put) finished well: " + str(result))

            event_details = 'Customer {} {}'.format(customer_uuid,
                                                    'enabled' if enable.enabled else 'disabled')
            utils.audit_trail('Change enable', request.transaction_id,
                              request.headers, customer_uuid,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("EnabledController - Failed to Change enable", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("EnabledController - change enable (put) - Failed to Change enable", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(None, str, rest_content_types='json')
    def post(self, customer_id):
            raise err_utils.get_error(request.transaction_id, status_code=405)

    @wsexpose(None, str, rest_content_types='json')
    def get(self, customer_id):
            raise err_utils.get_error(request.transaction_id, status_code=405)

    @wsexpose(None, str, rest_content_types='json')
    def delete(self, customer_id):
            raise err_utils.get_error(request.transaction_id, status_code=405)
