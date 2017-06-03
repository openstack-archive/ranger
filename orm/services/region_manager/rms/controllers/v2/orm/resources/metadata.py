import json

import logging

from pecan import rest, request
import wsme
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

from rms.services import error_base
from rms.services import services as RegionService

from rms.utils import authentication

from orm_common.utils import api_error_utils as err_utils
from orm_common.utils import utils

logger = logging.getLogger(__name__)


class MetaData(wtypes.DynamicBase):
    """main json header."""

    metadata = wsme.wsattr({str: [str]}, mandatory=True)

    def __init__(self, metadata={}):
        """init function.

        :param regions:
        :return:
        """
        self.metadata = metadata


class RegionMetadataController(rest.RestController):

    @wsexpose(MetaData, str, status_code=200, rest_content_types='json')
    def get(self, region_id):
        logger.info("Get metadata for region id: {}".format(region_id))
        authentication.authorize(request, 'metadata:get')

        try:
            region = RegionService.get_region_by_id_or_name(region_id)
            logger.debug("Got region metadata: {}".format(region.metadata))
            return MetaData(region.metadata)

        except error_base.ErrorStatus as exp:
            logger.error("RegionsController - {}".format(exp.message))
            raise err_utils.get_error(request.transaction_id,
                                      message=exp.message,
                                      status_code=exp.status_code)
        except Exception as exp:
            logger.exception(exp.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exp.message)

    @wsexpose(MetaData, str, body=MetaData, status_code=201,
              rest_content_types='json')
    def post(self, region_id, metadata_input):
        """Handle post request.
        :param region_id: region_id to add metadata to.
        :param metadata_input: json data
        :return: 201 created on success, 409 duplicate entry, 404 not found
        """
        logger.info("Entered Create region metadata")
        logger.debug("Got metadata: {}".format(metadata_input))
        authentication.authorize(request, 'metadata:create')

        try:
            self._validate_request_input()
            # May raise an exception which will return status code 400
            result = RegionService.add_region_metadata(region_id,
                                                       metadata_input.metadata)
            logger.debug("Metadata was successfully added to "
                         "region: {}. New metadata: {}".format(region_id, result))

            event_details = 'Region {} metadata added'.format(region_id)
            utils.audit_trail('create metadata', request.transaction_id,
                              request.headers, region_id,
                              event_details=event_details)
            return MetaData(result)

        except error_base.ErrorStatus as e:
            logger.error(e.message)
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=e.status_code)
        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(MetaData, str, body=MetaData, status_code=201,
              rest_content_types='json')
    def put(self, region_id, metadata_input):
        """Handle put request.
        :param region_id: region_id to update metadata to.
        :param metadata_input: json data
        :return: 201 created on success, 404 not found
        """
        logger.info("Entered update region metadata")
        logger.debug("Got metadata: {}".format(metadata_input))
        authentication.authorize(request, 'metadata:update')

        try:
            self._validate_request_input()
            # May raise an exception which will return status code 400
            result = RegionService.update_region_metadata(region_id,
                                                          metadata_input.metadata)
            logger.debug("Metadata was successfully added to "
                         "region: {}. New metadata: {}".format(region_id, result))

            event_details = 'Region {} metadata updated'.format(region_id)
            utils.audit_trail('update metadata', request.transaction_id,
                              request.headers, region_id,
                              event_details=event_details)
            return MetaData(result)

        except error_base.ErrorStatus as e:
            logger.error(e.message)
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=e.status_code)
        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    @wsexpose(None, str, str, status_code=204, rest_content_types='json')
    def delete(self, region_id, metadata_key):
        """Handle delete request.
        :param region_id: region_id to update metadata to.
        :param metadata_key: metadata key to be deleted
        :return: 204 deleted
        """
        logger.info("Entered delete region metadata with "
                    "key: {}".format(metadata_key))
        authentication.authorize(request, 'metadata:delete')

        try:
            # May raise an exception which will return status code 400
            result = RegionService.delete_metadata_from_region(region_id,
                                                               metadata_key)
            logger.debug("Metadata was successfully deleted.")

            event_details = 'Region {} metadata {} deleted'.format(
                region_id, metadata_key)
            utils.audit_trail('delete metadata', request.transaction_id,
                              request.headers, region_id,
                              event_details=event_details)

        except error_base.ErrorStatus as e:
            logger.error(e.message)
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=e.status_code)
        except Exception as exception:
            logger.error(exception.message)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=exception.message)

    def _validate_request_input(self):
        data_dict = json.loads(request.body)
        logger.debug("Got {}".format(data_dict))
        for k, v in data_dict['metadata'].iteritems():
            if isinstance(v, basestring):
                logger.error("Invalid json. value type list is expected, "
                             "received string, for metadata key {}".format(k))
                raise error_base.ErrorStatus(400, "Invalid json. Expecting list "
                                                  "of metadata values, got string")
