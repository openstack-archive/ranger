from cms_rest.controllers.v1.orm.configuration import ConfigurationController
from cms_rest.controllers.v1.orm.customer.root import CustomerController
from cms_rest.controllers.v1.orm.logs import LogsController
from pecan.rest import RestController


class OrmController(RestController):
    configuration = ConfigurationController()
    customers = CustomerController()
    logs = LogsController()
