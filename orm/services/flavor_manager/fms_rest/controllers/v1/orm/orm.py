from fms_rest.controllers.v1.orm.configuration import ConfigurationController
from fms_rest.controllers.v1.orm.flavors.flavors import FlavorController
from fms_rest.controllers.v1.orm.logs import LogsController
from pecan.rest import RestController


class OrmController(RestController):

    configuration = ConfigurationController()
    flavors = FlavorController()
    logs = LogsController()
