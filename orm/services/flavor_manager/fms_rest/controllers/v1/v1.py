from __future__ import absolute_import

from orm.services.flavor_manager.fms_rest.controllers.v1.orm.orm import OrmController

from pecan.rest import RestController


class V1Controller(RestController):

    orm = OrmController()
