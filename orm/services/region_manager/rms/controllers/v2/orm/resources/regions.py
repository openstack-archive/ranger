"""rest module."""
import logging
import wsme

from orm_common.utils import api_error_utils as err_utils
from orm_common.utils import utils
from pecan import request, rest
from rms.controllers.v2.orm.resources.metadata import RegionMetadataController
from rms.controllers.v2.orm.resources.status import RegionStatusController
from rms.model import model as PythonModel
from rms.model import url_parm
from rms.services import error_base
from rms.services import services as RegionService
from rms.utils import authentication
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

logger = logging.getLogger(__name__)


class Address(wtypes.DynamicBase):
    """wsme class for address json."""

    country = wsme.wsattr(wtypes.text, mandatory=True)
    state = wsme.wsattr(wtypes.text, mandatory=True)
    city = wsme.wsattr(wtypes.text, mandatory=True)
    street = wsme.wsattr(wtypes.text, mandatory=True)
    zip = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, country=None, state=None, city=None,
                 street=None, zip=None):
        """Init function

        :param country:
        :param state:
        :param city:
        :param street:
        :param zip:
        """
        self.country = country
        self.state = state
        self.city = city
        self.street = street
        self.zip = zip

    def _to_clean_python_obj(self):
        obj = PythonModel.Address()
        obj.country = self.country
        obj.state = self.state
        obj.city = self.city
        obj.street = self.street
        obj.zip = self.zip
        return obj


class EndPoint(wtypes.DynamicBase):
    """class method endpoints body."""

    publicurl = wsme.wsattr(wtypes.text, mandatory=True, name="publicURL")
    type = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, publicurl=None, type=None):
        """init function.

        :param publicURL: field
        :param typee: field
        :return:
        """
        self.type = type
        self.publicurl = publicurl

    def _to_clean_python_obj(self):
        obj = PythonModel.EndPoint()
        obj.publicurl = self.publicurl
        obj.type = self.type
        return obj


class RegionsData(wtypes.DynamicBase):
    """class method json header."""

    status = wsme.wsattr(wtypes.text, mandatory=True)
    id = wsme.wsattr(wtypes.text, mandatory=True)
    name = wsme.wsattr(wtypes.text, mandatory=False)
    ranger_agent_version = wsme.wsattr(wtypes.text, mandatory=True, name="rangerAgentVersion")
    open_stack_version = wsme.wsattr(wtypes.text, mandatory=True, name="OSVersion")
    clli = wsme.wsattr(wtypes.text, mandatory=True, name="CLLI")
    metadata = wsme.wsattr({str: [str]}, mandatory=True)
    endpoints = wsme.wsattr([EndPoint], mandatory=True)
    address = wsme.wsattr(Address, mandatory=True)
    design_type = wsme.wsattr(wtypes.text, mandatory=True, name="designType")
    location_type = wsme.wsattr(wtypes.text, mandatory=True, name="locationType")
    vlcp_name = wsme.wsattr(wtypes.text, mandatory=True, name="vlcpName")

    def __init__(self, status=None, id=None, name=None, clli=None, design_type=None,
                 location_type=None, vlcp_name=None, open_stack_version=None,
                 address=Address(), ranger_agent_version=None, metadata={},
                 endpoint=[EndPoint()]):
        """init function

        :param status:
        :param id:
        :param name:
        :param clli:
        :param design_type:
        :param location_type:
        :param vlcp_name:
        :param open_stack_version:
        :param address:
        :param ranger_agent_version:
        :param metadata:
        :param endpoint:
        """
        self.status = status
        self.id = id
        self.name = self.id
        self.clli = clli
        self.ranger_agent_version = ranger_agent_version
        self.metadata = metadata
        self.endpoint = endpoint
        self.design_type = design_type
        self.location_type = location_type
        self.vlcp_name = vlcp_name
        self.address = address
        self.open_stack_version = open_stack_version

    def _to_clean_python_obj(self):
        obj = PythonModel.RegionData()
        obj.endpoints = []
        obj.status = self.status
        obj.id = self.id
        obj.name = self.id
        obj.ranger_agent_version = self.ranger_agent_version
        obj.clli = self.clli
        obj.metadata = self.metadata
        for endpoint in self.endpoints:
            obj.endpoints.append(endpoint._to_clean_python_obj())
        obj.address = self.address._to_clean_python_obj()
        obj.design_type = self.design_type
        obj.location_type = self.location_type
        obj.vlcp_name = self.vlcp_name
        obj.open_stack_version = self.open_stack_version
        return obj


class Regions(wtypes.DynamicBase):
    """main json header."""

    regions = wsme.wsattr([RegionsData], mandatory=True)

    def __init__(self, regions=[RegionsData()]):
        """init function.

        :param regions:
        :return:
        """
        self.regions = regions


class RegionsController(rest.RestController):
    """controller get resource."""
    metadata = RegionMetadataController()
    status = RegionStatusController()

    @wsexpose(Regions, str, str, [str], str, str, str, str, str, str, str,
              str, str, str, status_code=200, rest_content_types='json')
    def get_all(self, type=None, status=None, metadata=None, rangerAgentVersion=None,
                clli=None, regionname=None, osversion=None, valet=None,
                state=None, country=None, city=None, street=None, zip=None):
        """get regions.

        :param type: query field
        :param status: query field
        :param metadata: query field
        :param rangerAgentVersion: query field
        :param clli: query field
        :param regionname: query field
        :param osversion: query field
        :param valet: query field
        :param state: query field
        :param country: query field
        :param city: query field
        :param street: query field
        :param zip: query field
        :return: json from db
        :exception: EntityNotFoundError 404
        """
        logger.info("Entered Get Regions")
        authentication.authorize(request, 'region:get_all')

        url_args = {'type': type, 'status': status, 'metadata': metadata,
                    'rangerAgentVersion': rangerAgentVersion, 'clli': clli, 'regionname': regionname,
                    'osversion': osversion, 'valet': valet, 'state': state,
                    'country': country, 'city': city, 'street': street, 'zip': zip}
        logger.debug("Parameters: {}".format(str(url_args)))

        try:
            url_args = url_parm.UrlParms(**url_args)

            result = RegionService.get_regions_data(url_args)

            logger.debug("Returning regions: {}".format(', '.join(
                [region.name for region in result.regions])))

            return result

        except error_base.ErrorStatus as e:
            logger.error("RegionsController {}".format(e.message))
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=e.status_code)

        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      message=exception.message)

    @wsexpose(RegionsData, str, status_code=200, rest_content_types='json')
    def get_one(self, id_or_name):
        logger.info("API: Entered get region by id or name: {}".format(id_or_name))
        authentication.authorize(request, 'region:get_one')

        try:
            result = RegionService.get_region_by_id_or_name(id_or_name)
            logger.debug("API: Got region {} success: {}".format(id_or_name, result))
        except error_base.ErrorStatus as exp:
            logger.error("RegionsController {}".format(exp.message))
            raise err_utils.get_error(request.transaction_id,
                                      message=exp.message,
                                      status_code=exp.status_code)
        except Exception as exp:
            logger.exception(exp.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exp.message)

        return result

    @wsexpose(RegionsData, body=RegionsData, status_code=201, rest_content_types='json')
    def post(self, full_region_input):
        logger.info("API: CreateRegion")
        authentication.authorize(request, 'region:create')

        try:
            logger.debug("API: create region .. data = : {}".format(full_region_input))
            result = RegionService.create_full_region(full_region_input)
            logger.debug("API: region created : {}".format(result))

            event_details = 'Region {} {} created: AICversion {}, OSversion {}, CLLI {}'.format(
                full_region_input.name, full_region_input.design_type,
                full_region_input.ranger_agent_version,
                full_region_input.open_stack_version, full_region_input.clli)
            utils.audit_trail('create region', request.transaction_id,
                              request.headers, full_region_input.id,
                              event_details=event_details)
        except error_base.InputValueError as exp:
            logger.exception("Error in save region {}".format(exp.message))
            raise err_utils.get_error(request.transaction_id,
                                      status_code=exp.status_code,
                                      message=exp.message)

        except error_base.ConflictError as exp:
            logger.exception("Conflict error {}".format(exp.message))
            raise err_utils.get_error(request.transaction_id,
                                      message=exp.message,
                                      status_code=exp.status_code)

        except Exception as exp:
            logger.exception("Error in creating region .. reason:- {}".format(exp))
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      message=exp.message)

        return result

    @wsexpose(None, str, rest_content_types='json', status_code=204)
    def delete(self, region_id):
        logger.info("Delete Region")
        authentication.authorize(request, 'region:delete')

        try:

            logger.debug("delete region {}".format(region_id))
            result = RegionService.delete_region(region_id)
            logger.debug("region deleted")

            event_details = 'Region {} deleted'.format(region_id)
            utils.audit_trail('delete region', request.transaction_id,
                              request.headers, region_id,
                              event_details=event_details)

        except Exception as exp:
            logger.exception(
                "error in deleting region .. reason:- {}".format(exp))
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      message=exp.message)
        return

    @wsexpose(RegionsData, str, body=RegionsData, status_code=201,
              rest_content_types='json')
    def put(self, region_id, region):
        logger.info("API: update region")
        authentication.authorize(request, 'region:update')

        try:

            logger.debug(
                "region to update {} with{}".format(region_id, region))
            result = RegionService.update_region(region_id, region)
            logger.debug("API: region {} updated".format(region_id))

            event_details = 'Region {} {} modified: AICversion {}, OSversion {}, CLLI {}'.format(
                region.name, region.design_type, region.ranger_agent_version,
                region.open_stack_version, region.clli)
            utils.audit_trail('update region', request.transaction_id,
                              request.headers, region_id,
                              event_details=event_details)

        except error_base.NotFoundError as exp:
            logger.exception("region {} not found".format(region_id))
            raise err_utils.get_error(request.transaction_id,
                                      status_code=exp.status_code,
                                      message=exp.message)

        except error_base.InputValueError as exp:
            logger.exception("not valid input {}".format(exp.message))
            raise err_utils.get_error(request.transaction_id,
                                      status_code=exp.status_code,
                                      message=exp.message)
        except Exception as exp:
            logger.exception(
                "API: error in updating region {}.. reason:- {}".format(region_id,
                                                                        exp))
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      message=exp.message)
        return result
