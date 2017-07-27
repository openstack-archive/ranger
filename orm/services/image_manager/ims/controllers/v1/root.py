"""V1 controller module."""
from ims.controllers.v1.orm import root


class V1Controller(object):
    """V1 root controller class."""

    orm = root.OrmController()
