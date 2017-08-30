"""Status (activate/deactivate) Image rest API input module."""

from orm.common.orm_common.injector import injector
from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.services.image_manager.ims.logger import get_logger
from orm.services.image_manager.ims.logic.error_base import ErrorStatus
from orm.services.image_manager.ims.persistency.wsme.models import Enabled, ImageWrapper
from orm.services.image_manager.ims.utils import authentication as auth

from pecan import request, rest
from wsmeext.pecan import wsexpose

di = injector.get_di()

LOG = get_logger(__name__)


@di.dependsOn('image_logic')
@di.dependsOn('utils')
class EnabledController(rest.RestController):
    """Status controller."""

    @wsexpose(ImageWrapper, str, body=Enabled, rest_content_types='json', status_code=200)
    def put(self, image_id, enabled):
        image_logic, utils = di.resolver.unpack(EnabledController)
        auth.authorize(request, "image:enable")
        try:
            LOG.info("EnabledController - received enabled = {}".format(enabled.enabled))
            result = image_logic.enable_image(image_id, enabled.enabled * 1, request.transaction_id)
            status = "activated"
            if not enabled.enabled:
                status = "deactivated"
            LOG.info("EnabledController - Image was successfully {}".format(status))

            event_details = 'Image {} {}'.format(
                image_id, 'active' if enabled.enabled else 'inactive')
            utils.audit_trail('activate image', request.transaction_id,
                              request.headers, image_id,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("Failed in EnableImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("Failed in EnableImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, body=Enabled, rest_content_types='json',
              status_code=200)
    def post(self, image_id, enabled):
        image_logic, utils = di.resolver.unpack(EnabledController)
        auth.authorize(request, "image:enable")
        try:
            LOG.debug("method not allowed only put allowed")
            raise ErrorStatus(405,
                              "method not allowed only 'put' method allowed")
            return None

        except ErrorStatus as exception:
            LOG.log_exception("Failed in EnableImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("Failed in EnableImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
