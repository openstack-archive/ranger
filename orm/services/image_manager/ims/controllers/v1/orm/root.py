"""ORM controller module."""
from ims.controllers.v1.orm.images import images


class OrmController(object):
    """ORM root controller class."""

    images = images.ImageController()
