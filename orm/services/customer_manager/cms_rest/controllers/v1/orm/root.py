from __future__ import absolute_import

from ..orm.configuration import ConfigurationController
from ..orm.customer.root import CustomerController
from ..orm.logs import LogsController
from pecan.rest import RestController


class OrmController(RestController):
    configuration = ConfigurationController()
    customers = CustomerController()
    logs = LogsController()
