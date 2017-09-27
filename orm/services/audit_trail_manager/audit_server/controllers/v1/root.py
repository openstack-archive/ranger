"""v1 controller module."""


from orm.services.audit_trail_manager.audit_server.controllers.v1 import audit


class V1Controller(object):
    """v1 controller."""

    audit = audit.AuditController()
