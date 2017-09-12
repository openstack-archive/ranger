"""V2 root controller module."""
from __future__ import absolute_import

from orm.services.region_manager.rms.controllers.v2.orm import root


class V2Controller(object):
    """V2 root controller class."""

    orm = root.OrmController()
