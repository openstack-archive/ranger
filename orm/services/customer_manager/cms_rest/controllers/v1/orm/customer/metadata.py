from cms_rest.logger import get_logger
from cms_rest.logic.error_base import ErrorStatus
import cms_rest.logic.metadata_logic as logic
from cms_rest.model.Models import CustomerResultWrapper, MetadataWrapper
from cms_rest.utils import authentication
from orm_common.utils import api_error_utils as err_utils
from orm_common.utils import utils
from pecan import request, rest
from wsmeext.pecan import wsexpose

LOG = get_logger(__name__)


class MetadataController(rest.RestController):
    @wsexpose(CustomerResultWrapper, str, body=MetadataWrapper, rest_content_types='json')
    def post(self, customer_uuid, metadata):
        authentication.authorize(request, 'customers:add_metadata')
        try:
            res = logic.add_customer_metadata(customer_uuid, metadata, request.transaction_id)

            event_details = 'Customer {} metadata added'.format(customer_uuid)
            utils.audit_trail('add customer metadata', request.transaction_id,
                              request.headers, customer_uuid,
                              event_details=event_details)
            return res
        except AttributeError as ex:
            raise err_utils.get_error(request.transaction_id,
                                      message=ex.message, status_code=409)
        except ValueError as ex:
            raise err_utils.get_error(request.transaction_id,
                                      message=ex.message, status_code=404)
        except ErrorStatus as ex:
            LOG.log_exception("MetaDataController - Failed to add metadata", ex)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=ex.status_code)
        except LookupError as ex:
            LOG.log_exception("MetaDataController - {0}".format(ex.message), ex)
            raise err_utils.get_error(request.transaction_id,
                                      message=ex.message, status_code=400)
        except Exception as ex:
            LOG.log_exception("MetaDataController - Failed to add metadata", ex)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500, error_details=str(ex))

    @wsexpose(CustomerResultWrapper, str, body=MetadataWrapper, rest_content_types='json')
    def put(self, customer_uuid, metadata):
        authentication.authorize(request, 'customers:update_metadata')
        try:
            res = logic.update_customer_metadata(customer_uuid, metadata, request.transaction_id)

            event_details = 'Customer {} metadata updated'.format(customer_uuid)
            utils.audit_trail('update customer metadata',
                              request.transaction_id, request.headers,
                              customer_uuid, event_details=event_details)
            return res
        except AttributeError as ex:
            raise err_utils.get_error(request.transaction_id,
                                      message=ex.message, status_code=400)
        except ValueError as ex:
            raise err_utils.get_error(request.transaction_id,
                                      message=ex.message, status_code=404)
        except ErrorStatus as ex:
            LOG.log_exception("MetaDataController - Failed to add metadata", ex)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=ex.status_code)
        except LookupError as ex:
            LOG.log_exception("MetaDataController - {0}".format(ex.message), ex)
            raise err_utils.get_error(request.transaction_id,
                                      message=ex.message, status_code=400)
        except Exception as ex:
            LOG.log_exception("MetaDataController - Failed to add metadata", ex)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500, error_details=str(ex))
