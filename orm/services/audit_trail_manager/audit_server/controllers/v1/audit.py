"""audit controller module."""

from audit_server.controllers.v1 import configuration
from audit_server.controllers.v1 import logs
from audit_server.controllers.v1 import transaction


class AuditController(object):
    """audit controller."""

    transaction = transaction.TransactionController()
    logs = logs.LogsController()
    configuration = configuration.ConfigurationController()
