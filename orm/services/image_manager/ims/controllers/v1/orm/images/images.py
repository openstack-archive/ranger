import oslo_db

from ims.controllers.v1.orm.images.customers import CustomerController
from ims.controllers.v1.orm.images.enabled import EnabledController
from ims.controllers.v1.orm.images.regions import RegionController
from ims.logger import get_logger
from ims.logic.error_base import ErrorStatus
from ims.persistency.wsme.models import ImageSummaryResponse, ImageWrapper
from ims.utils import authentication as auth
from orm_common.injector import injector
from orm_common.utils import api_error_utils as err_utils
from pecan import request, rest
from wsmeext.pecan import wsexpose

di = injector.get_di()
LOG = get_logger(__name__)


@di.dependsOn('image_logic')
@di.dependsOn('utils')
class ImageController(rest.RestController):
    regions = RegionController()
    customers = CustomerController()
    enabled = EnabledController()

    @wsexpose(ImageWrapper, str, body=ImageWrapper, rest_content_types='json', status_code=201)
    def post(self, invalid_extra_param=None, image_wrapper=None):
        image_logic, utils = di.resolver.unpack(ImageController)
        uuid = "FailedToGetFromUUIDGen"
        auth.authorize(request, "image:create")

        if not image_wrapper:
            raise err_utils.get_error(request.transaction_id,
                                      message="Body not supplied",
                                      status_code=400)

        if invalid_extra_param:
            raise err_utils.get_error(request.transaction_id,
                                      message="URL has invalid extra param '{}' ".format(invalid_extra_param),
                                      status_code=405)
        try:
            LOG.info("ImageController - Create image: " + str(image_wrapper.image.name))
            image_wrapper.image.owner = request.headers.get('X-RANGER-Owner') or ''

            if not image_wrapper.image.id:
                uuid = utils.make_uuid()
            else:
                try:
                    uuid = utils.create_existing_uuid(image_wrapper.id)
                except TypeError:
                    raise ErrorStatus(409.1, message='Image UUID already exists')

            try:
                ret_image = image_logic.create_image(image_wrapper, uuid,
                                                     request.transaction_id)
            except oslo_db.exception.DBDuplicateEntry as exception:
                raise ErrorStatus(409.2, 'The field {0} already exists'.format(exception.columns))

            LOG.info("ImageController - Image Created: " + str(ret_image))

            event_details = 'Image {} {} {}, visibility: {}, created in regions: {} with tenants: {}'.format(
                uuid, image_wrapper.image.name, image_wrapper.image.url,
                image_wrapper.image.visibility,
                [r.name for r in image_wrapper.image.regions],
                image_wrapper.image.customers)
            utils.audit_trail('create image', request.transaction_id,
                              request.headers, uuid,
                              event_details=event_details)
            return ret_image

        except ErrorStatus as exception:
            LOG.log_exception("ImageController - Failed to CreateImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("ImageController - Failed to CreateImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(ImageWrapper, str, body=ImageWrapper, rest_content_types='json', status_code=200)
    def put(self, image_id, image_wrapper):
        image_logic, utils = di.resolver.unpack(ImageController)
        auth.authorize(request, "image:update")
        try:
            LOG.info("ImageController - UpdateImage: " + str(image_wrapper.image.name))
            try:
                result = image_logic.update_image(image_wrapper, image_id,
                                                  request.transaction_id)
            except oslo_db.exception.DBDuplicateEntry as exception:
                raise ErrorStatus(409.2, 'The field {0} already exists'.format(exception.columns))

            LOG.info("ImageController - UpdateImage finished well: " + str(image_wrapper.image.name))

            event_details = 'Image {} {} {}, visibility: {}, created in regions: {} with tenants: {}'.format(
                image_id, image_wrapper.image.name, image_wrapper.image.url,
                image_wrapper.image.visibility,
                [r.name for r in image_wrapper.image.regions],
                image_wrapper.image.customers)
            utils.audit_trail('update image', request.transaction_id,
                              request.headers, image_id,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("Failed in UpdateImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("ImageController - Failed to UpdateImage", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(ImageWrapper, str, str, str, str, str, rest_content_types='json')
    def get(self, image_uuid):
        image_logic, utils = di.resolver.unpack(ImageController)
        LOG.info("ImageController - GetImageDetails: uuid is {}".format(
            image_uuid))
        auth.authorize(request, "image:get_one")

        try:
            return image_logic.get_image_by_uuid(image_uuid)

        except ErrorStatus as exception:
            LOG.log_exception("ImageController - Failed to GetImageDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("ImageController - Failed to GetImageDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(ImageSummaryResponse, str, str, str, rest_content_types='json')
    def get_all(self, visibility=None, region=None, tenant=None):
        image_logic, utils = di.resolver.unpack(ImageController)
        auth.authorize(request, "image:list")

        try:
            LOG.info("ImageController - GetImagelist")

            result = image_logic.get_image_list_by_params(visibility, region, tenant)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("ImageController - Failed to GetImagelist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("ImageController - Failed to GetImagelist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, rest_content_types='json', status_code=204)
    def delete(self, image_uuid):
        image_logic, utils = di.resolver.unpack(ImageController)
        LOG.info("Got image delete request")
        auth.authorize(request, "image:delete")
        try:
            LOG.info("ImageController - delete image: image id:" + image_uuid)
            image_logic.delete_image_by_uuid(image_uuid, request.transaction_id)
            LOG.info("ImageController - delete image finished well: ")

            event_details = 'Image {} deleted'.format(image_uuid)
            utils.audit_trail('delete image', request.transaction_id,
                              request.headers, image_uuid,
                              event_details=event_details)

        except ErrorStatus as exp:
            LOG.log_exception("ImageController - Failed to delete image", exp)
            raise err_utils.get_error(request.transaction_id,
                                      message=exp.message,
                                      status_code=exp.status_code)

        except Exception as exp:
            LOG.log_exception("ImageController - Failed to delete image", exp)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exp))

    '''
    @expose()
    def _lookup(self, primary_key, *remainder):
        #
        # This function is called when pecan does not find controller for the request
        #
        abort(405, "Invalid URL")
    '''
