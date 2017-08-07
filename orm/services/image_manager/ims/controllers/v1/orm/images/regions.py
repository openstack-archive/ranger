from ims.controllers.v1.orm.images.metadata import MetadataController
from ims.logger import get_logger
from ims.logic.error_base import ErrorStatus
from ims.persistency.wsme.models import RegionWrapper
from ims.utils import authentication as auth
from orm_common.injector import injector
from orm_common.utils import api_error_utils as err_utils
from pecan import request, rest
from wsmeext.pecan import wsexpose

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('image_logic')
@di.dependsOn('utils')
class RegionController(rest.RestController):
    metadata = MetadataController()

    @wsexpose([str], str, rest_content_types='json')
    def get(self, image_id):
        # get region has been unfeatured
        raise err_utils.get_error(request.transaction_id,
                                  status_code=405)

    @wsexpose(RegionWrapper, str, body=RegionWrapper, rest_content_types='json', status_code=201)
    def post(self, image_id, region_wrapper):  # add regions to image
        image_logic, utils = di.resolver.unpack(RegionController)
        auth.authorize(request, "region:create")

        try:
            if not region_wrapper.regions:
                raise ErrorStatus(400,
                                  " bad resquest please provide correct json")
            LOG.info("RegionController - add regions: " + str(region_wrapper))

            result = image_logic.add_regions(image_id, region_wrapper, request.transaction_id)

            LOG.info("RegionController - regions added: " + str(result))

            event_details = 'Image {} regions: {} added'.format(
                image_id, [r.name for r in region_wrapper.regions])
            utils.audit_trail('add regions', request.transaction_id,
                              request.headers, image_id,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("RegionController - Failed to add region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("RegionController - Failed to add region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(RegionWrapper, str, body=RegionWrapper, rest_content_types='json', status_code=200)
    def put(self, image_id, region_wrapper):  # add regions to image
        image_logic, utils = di.resolver.unpack(RegionController)
        auth.authorize(request, "region:update")
        try:
            if not region_wrapper.regions:
                raise ErrorStatus(400,
                                  " bad resquest please provide correct json")
            LOG.info("RegionController - replace regions: " + str(region_wrapper))

            result = image_logic.replace_regions(image_id, region_wrapper, request.transaction_id)

            LOG.info("RegionController - regions replaced: " + str(result))

            event_details = 'Image {} regions: {} updated'.format(
                image_id, [r.name for r in region_wrapper.regions])
            utils.audit_trail('replace regions', request.transaction_id,
                              request.headers, image_id,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("RegionController - Failed to replace region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("RegionController - Failed to replace region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(None, str, str, rest_content_types='json', status_code=204)
    def delete(self, image_id, region_name):
        image_logic, utils = di.resolver.unpack(RegionController)
        auth.authorize(request, "region:delete")
        try:
            LOG.info("RegionController - delete region: " + str(region_name))

            result = image_logic.delete_region(image_id, region_name, request.transaction_id)

            LOG.info("RegionController - region deleted: " + str(result))

            event_details = 'Image {} region {} deleted'.format(image_id,
                                                                region_name)
            utils.audit_trail('delete region', request.transaction_id,
                              request.headers, image_id,
                              event_details=event_details)

        except ErrorStatus as exception:  # include NotFoundError
            LOG.log_exception("RegionController - Failed to delete region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)
        except Exception as exception:
            LOG.log_exception("RegionController - Failed to delete region", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)
