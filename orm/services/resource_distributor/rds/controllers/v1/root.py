"""v1 controller."""
from rds.controllers.v1 import logs
from rds.controllers.v1.configuration import root as config_root
from rds.controllers.v1.resources import root as Rds

from rds.controllers.v1.status import resource_status


class RDS(object):
    """RDS controller."""

    resources = Rds.CreateNewResource()
    status = resource_status.Status()
    configuration = config_root.Configuration()
    logs = logs.LogsController()


class V1Controller(object):
    """v1 controller."""

    rds = RDS
