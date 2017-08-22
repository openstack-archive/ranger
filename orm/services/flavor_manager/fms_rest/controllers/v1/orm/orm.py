from __future__ import absolute_import

from orm.services.flavor_manager.fms_rest.controllers.v1.orm.configuration import ConfigurationController
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.flavors.flavors import FlavorController
from orm.services.flavor_manager.fms_rest.controllers.v1.orm.logs import LogsController

from pecan.rest import RestController


class OrmController(RestController):

    configuration = ConfigurationController()
    flavors = FlavorController()
    logs = LogsController()
