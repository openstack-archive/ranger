from __future__ import absolute_import

from orm.services.image_manager.ims.controllers.v1.orm.orm import OrmController

from pecan.rest import RestController


class V1Controller(RestController):

    orm = OrmController()
