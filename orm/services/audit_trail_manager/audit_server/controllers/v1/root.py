"""v1 controller module."""


from audit_server.controllers.v1 import audit


class V1Controller(object):
    """v1 controller."""

    audit = audit.AuditController()
