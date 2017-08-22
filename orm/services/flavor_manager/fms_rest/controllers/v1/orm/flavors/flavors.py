from __future__ import absolute_import

from orm.common.orm_common.injector import injector
from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors.os_extra_specs import OsExtraSpecsController
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors.regions import RegionController
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors.tags import TagsController
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors.tenants import TenantController
from orm.services.flavor_manager.fms_rest.data.wsme.models import FlavorListFullResponse, FlavorWrapper
from orm.services.flavor_manager.fms_rest.logger import get_logger
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus
from orm.services.flavor_manager.fms_rest.utils import authentication

from pecan import request, rest
from wsmeext.pecan import wsexpose

di = injector.get_di()
LOG = get_logger(__name__)


@di.dependsOn('flavor_logic')
@di.dependsOn('utils')
class FlavorController(rest.RestController):

    regions = RegionController()
    tenants = TenantController()
    os_extra_specs = OsExtraSpecsController()
    extra_specs = OsExtraSpecsController()
    tags = TagsController()

    @wsexpose(FlavorWrapper, body=FlavorWrapper, rest_content_types='json', status_code=201)
    def post(self, flavors):
        flavor_logic, utils = di.resolver.unpack(FlavorController)
        uuid = "FailedToGetFromUUIDGen"
        LOG.info("FlavorController - Createflavor: " + str(flavors))
        authentication.authorize(request, 'flavor:create')

        try:

            if not flavors.flavor.id:
                uuid = utils.make_uuid()
            else:
                try:
                    uuid = utils.create_existing_uuid(
                        flavor_logic.get_fixed_uuid(flavors.flavor.id))
                except TypeError:
                    LOG.error("UUID already exist")
                    raise ErrorStatus(409, 'UUID already exists')

            result = flavor_logic.create_flavor(flavors, uuid, request.transaction_id)

            LOG.info("FlavorController - Flavor Created: " + str(result))

            event_details = 'Flavor {} created in regions: {}, tenants: {} with visibility: {}'.format(
                uuid, [r.name for r in flavors.flavor.regions],
                flavors.flavor.tenants, flavors.flavor.visibility)
            utils.audit_trail('create flavor', request.transaction_id,
                              request.headers, uuid,
                              event_details=event_details)
            return result

        except ErrorStatus as exception:
            LOG.log_exception("FlavorController - Failed to CreateFlavor", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except ValueError as exception:
            LOG.log_exception("FlavorController - Failed to CreateFlavor", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=400,
                                      error_details=exception.message)

        except Exception as exception:
            LOG.log_exception("FlavorController - Failed to CreateFlavor", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(FlavorWrapper, str, body=FlavorWrapper, rest_content_types='json')
    def put(self, flavor_id, flavors):
        # update flavor is not featured
        raise err_utils.get_error(request.transaction_id,
                                  status_code=405)

    @wsexpose(FlavorWrapper, str, rest_content_types='json')
    def get(self, flavor_uuid_or_name):
        flavor_logic, utils = di.resolver.unpack(FlavorController)
        LOG.info("FlavorController - GetFlavorDetails: uuid or name is " + flavor_uuid_or_name)
        authentication.authorize(request, 'flavor:get_one')

        try:
            result = flavor_logic.get_flavor_by_uuid_or_name(flavor_uuid_or_name)
            LOG.info("FlavorController - GetFlavorDetails finished well: " + str(result))
            return result

        except ErrorStatus as exception:
            LOG.log_exception("FlavorController - Failed to GetFlavorDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("FlavorController - Failed to GetFlavorDetails", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(FlavorListFullResponse, str, str, str, str, str, str, str, rest_content_types='json')
    def get_all(self, visibility=None, region=None, tenant=None, series=None,
                starts_with=None, contains=None, alias=None):
        flavor_logic, utils = di.resolver.unpack(FlavorController)
        LOG.info("FlavorController - GetFlavorlist")
        authentication.authorize(request, 'flavor:get_all')

        try:
            result = flavor_logic.get_flavor_list_by_params(visibility, region,
                                                            tenant, series, starts_with, contains, alias)

            return result
        except ErrorStatus as exception:
            LOG.log_exception("FlavorController - Failed to GetFlavorlist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("FlavorController - Failed to GetFlavorlist", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

    @wsexpose(None, str, rest_content_types='json', status_code=204)
    def delete(self, flavor_uuid=None):
        authentication.authorize(request, 'flavor:delete')
        flavor_logic, utils = di.resolver.unpack(FlavorController)

        try:
            LOG.info("FlavorController - delete: uuid is " + flavor_uuid)
            flavor_logic.delete_flavor_by_uuid(flavor_uuid)
            LOG.info("FlavorController - delete flavor finished well")

            event_details = 'Flavor {} deleted'.format(flavor_uuid)
            utils.audit_trail('delete flavor by uuid', request.transaction_id,
                              request.headers, flavor_uuid,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("FlavorController - Failed to delete flavor", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except Exception as exception:
            LOG.log_exception("FlavorController - Failed to delete flavor", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
