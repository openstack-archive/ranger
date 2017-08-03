"""handle rest api input module."""

import ast
import logging.handlers
import time

import pecan
import wsme
from pecan import rest
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

from rds.controllers.v1.base import ClientSideError
from rds.controllers.v1.base import LockedEntity
from rds.controllers.v1.base import NotAllowedError
from rds.services import resource as ResourceService
from rds.services.base import ConflictValue

my_logger = logging.getLogger(__name__)

resources_operation_list = {
    "flavor": ['delete', 'create', 'modify'],
    "image": ['delete', 'create', 'modify']
}


class Links(wtypes.DynamicBase):
    """class method."""

    self = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(own, self=""):
        """init function.

        :param self: self link
        """
        own.self = self


class CreatedResource(wtypes.DynamicBase):
    """class method for returned json."""

    id = wsme.wsattr(wtypes.text, mandatory=True)
    created = wsme.wsattr(wtypes.text, mandatory=False)
    links = wsme.wsattr(Links, mandatory=True)
    updated = wsme.wsattr(wtypes.text, mandatory=False)
    err = wsme.wsattr(wtypes.text, mandatory=False)
    message = wsme.wsattr(wtypes.text, mandatory=False)

    def __init__(self, id="", err=None, message=None,
                 created=None, updated=None, links=Links()):
        """init function.

        :param id: resource id
        :param err: error if any
        :param message: error message
        :param created: timestamp
        :param updated: timestamp when put request
        :param links:
        """
        self.id = id
        self.links = links
        if created is not None:
            self.created = created
        if updated is not None:
            self.updated = updated
        if err is not None:
            self.err = err            # pragma: no cover
        if message is not None:
            self.message = message    # pragma: no cover


class Result(wtypes.DynamicBase):
    """class method, json header."""

    customer = wsme.wsattr(CreatedResource, mandatory=False)
    flavor = wsme.wsattr(CreatedResource, mandatory=False)
    image = wsme.wsattr(CreatedResource, mandatory=False)

    def __init__(self, customer=None,
                 flavor=None, image=None):
        """init function.

        :param customer: json header
        :param flavor: json header
        """
        if customer is not None:
            self.customer = customer
        if flavor is not None:
            self.flavor = flavor
        if image is not None:
            self.image = image


class TrackingData(wtypes.DynamicBase):
    """class method to handle json input."""

    external_id = wsme.wsattr(wtypes.text, mandatory=True)
    tracking_id = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, external_id="", tracking_id=""):
        """init function.

        :param external_id: full flow traking id
        :param tracking_id: enternal traking id
        """
        self.external_id = external_id
        self.tracking_id = tracking_id


class ResourceTypeData(wtypes.DynamicBase):
    """class method, handle json input."""

    resource_type = wsme.wsattr(wtypes.text, mandatory=True)
    resource_id = wsme.wsattr(wtypes.text, mandatory=False)

    def __init__(self, resource_type="", resource_id=None):
        """init function.

        :param resource_type: type of the resource eg.customer, flavor..
        :param resource_id: id of the resource
        """
        self.resource_type = resource_type
        if resource_id is not None:
            self.resource_id = resource_id    # pragma: no cover


class ResourceData(wtypes.DynamicBase):
    """class method to handle resource data json."""

    resource = wsme.wsattr(ResourceTypeData, mandatory=True)
    model = wsme.wsattr(wtypes.text, mandatory=True)
    # model = wsme.wsattr(FullJson, mandatory=True)
    tracking = wsme.wsattr(TrackingData, mandatory=True)

    def __init__(self, model="", resource=ResourceTypeData(),
                 tracking=TrackingData(),):
        """init function.

        :param model: input json (resource data)
        :param resource: resource type, resource id
        :param tracking: transaction id
        """
        self.resource = resource
        self.tracking = tracking
        self.model = model


class Resource(wtypes.DynamicBase):
    """main class  first key json."""

    service_template = wsme.wsattr(ResourceData, mandatory=True)

    def __init__(self, service_template=ResourceData()):
        """init function.

        :param service_template:
        """
        self.service_template = service_template


class CreateNewResource(rest.RestController):
    """creatin new resource controller."""

    @wsexpose(Result, body=Resource, status_code=201,
              rest_content_types='json')
    def post(self, resource):
        """Handle HTTP POST request.

        :param Customer (json in request body):
        :return: result (json format ... {'Cusetomer':{'id':'',
        'links':{'own':'how host url'},'created':'1234567890'}}
        the response will be 201 created if success
        :return 409 for conflict
        :return 400 bad request
        handle json input
        """
        my_logger.info("create resource")
        jsondata = resource.service_template.model
        my_logger.debug("parse json & get yaml file!!! {}".format(jsondata))
        uuid = resource.service_template.tracking.tracking_id
        resource_type = resource.service_template.resource.resource_type
        base_url = pecan.request.application_url
        jsondata = ast.literal_eval(jsondata)

        try:
            resource_id = ResourceService.main(jsondata,
                                               uuid,
                                               resource_type,
                                               'create')
            site_link = "%s/v1/rds/%s/%s" % (base_url,
                                             resource_type,
                                             resource_id)
            res = Result(**{resource_type: CreatedResource(id=resource_id,
                                                           created='%d' % (time.time() * 1000),
                                                           links=Links(site_link))})
            return res
        except ConflictValue as e:
            my_logger.error("the request blocked need to wait "
                            "for previous operation to be done ")
            raise LockedEntity(e.message)
        except Exception as e:
            my_logger.error("error :- %s " % str(e.message))
            raise ClientSideError(e.message)

    @wsexpose(Result, body=Resource, status_code=201,
              rest_content_types='json')
    def put(self, resource):
        """Handle HTTP POST request.

        :param Customer (json in request body):
        :return: result (json format ... {'Cusetomer':{'id':'',
        'links':{'own':'how host url'},'created':'1234567890'}}
        the response will be 201 created if success
        :return 409 for conflict
        :return 400 bad request
        handle json input
        """
        my_logger.info("modify resource")
        jsondata = resource.service_template.model
        my_logger.debug("parse json & get yaml file!!! {}".format(jsondata))
        uuid = resource.service_template.tracking.tracking_id
        resource_type = resource.service_template.resource.resource_type
        base_url = pecan.request.application_url
        jsondata = ast.literal_eval(jsondata)

        try:
            resource_id = ResourceService.main(jsondata,
                                               uuid,
                                               resource_type,
                                               'modify')
            my_logger.debug("data sent!.")
            site_link = "%s/v1/rds/%s/%s" % (base_url,
                                             resource_type,
                                             resource_id)
            res = Result(**{
                resource_type: CreatedResource(
                    id=resource_id,
                    updated='%d' % (time.time() * 1000),
                    links=Links(site_link))})
            return res
        except ConflictValue as e:
            my_logger.error("the request blocked need to wait "
                            "for previous operation to be done ")
            raise LockedEntity(e.message)
        except Exception as e:
            my_logger.error("error :- %s " % str(e.message))
            raise ClientSideError(e.message)

    @wsexpose(str, body=Resource, status_code=200,
              rest_content_types='json')
    def delete(self, resource):
        """handle json input.

        :param resource: input json
        :return: 200 if valid json
        :return: 405 not allowed for not valid resource to delete
        :return: 400 for bad request
        """
        operation = 'delete'
        my_logger.info("delete resource ")
        jsondata = resource.service_template.model
        my_logger.debug("parse json & get yaml file!!! {}".format(jsondata))
        jsondata = ast.literal_eval(jsondata)
        resource_uuid = resource.service_template.tracking.tracking_id
        resource_type = resource.service_template.resource.resource_type
        if resource_type not in resources_operation_list or operation not in \
                resources_operation_list[resource_type]:
            raise NotAllowedError("delete Not allowed for this"
                                  " resource %s" % resource_type)
        try:
            resource_id = ResourceService.main(jsondata,
                                               resource_uuid,
                                               resource_type,
                                               operation)
            return resource_id
        except ConflictValue as e:
            my_logger.error("the request blocked need to wait"
                            " for previous operation to be done ")
            raise LockedEntity(e.message)
        except Exception as e:
            my_logger.error("error :- %s " % str(e.message))
            raise ClientSideError(e.message)
