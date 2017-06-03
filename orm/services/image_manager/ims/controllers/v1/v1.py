from ims.controllers.v1.orm.orm import OrmController
from pecan.rest import RestController


class V1Controller(RestController):

    orm = OrmController()
