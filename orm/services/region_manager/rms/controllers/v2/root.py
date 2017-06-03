"""V2 root controller module."""
from rms.controllers.v2.orm import root


class V2Controller(object):
    """V2 root controller class."""

    orm = root.OrmController()
