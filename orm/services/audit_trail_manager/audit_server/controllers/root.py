"""root controller module."""


from orm.services.audit_trail_manager.audit_server.controllers.v1 import root as v1


class RootController(object):
    """root controller."""

    v1 = v1.V1Controller()
