from pecan import rest, request, response
from wsmeext.pecan import wsexpose
from ims.persistency.wsme.models import MetadataWrapper

from orm_common.injector import injector

from ims.logic.error_base import ErrorStatus

from ims.logger import get_logger
from orm_common.utils import api_error_utils as err_utils
from ims.utils import authentication as auth

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('metadata_logic')
@di.dependsOn('utils')
class MetadataController(rest.RestController):
    @wsexpose(str, str, str, body=MetadataWrapper, rest_content_types='json', status_code=200)
    def post(self, image_id, region_name, metadata_wrapper):  # add metadata to region
        metadata_logic, utils = di.resolver.unpack(MetadataController)
        auth.authorize(request, "metadata:create")

        try:
            LOG.info("MetadataController - add metadata: " + str(metadata_wrapper))

            metadata_logic.add_metadata(image_id, region_name, metadata_wrapper)

            LOG.info("MetadataController - metadata added")
            return "OK"

        except ErrorStatus as exception:
            LOG.log_exception("MetadataController - Failed to add metadata", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("MetadataController - Failed to add metadata", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)
