"""ORM controller module."""
from rms.controllers.v2.orm.resources import groups, regions


class OrmController(object):
    """ORM controller class."""

    regions = regions.RegionsController()
    groups = groups.GroupsController()
