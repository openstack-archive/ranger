from __future__ import absolute_import

from ..orm.configuration import ConfigurationController
from ..orm.customer.root import CustomerController
from ..orm.group.root import GroupController
from ..orm.logs import LogsController
from pecan.rest import RestController


class OrmController(RestController):
    configuration = ConfigurationController()
    customers = CustomerController()
    groups = GroupController()
    logs = LogsController()
