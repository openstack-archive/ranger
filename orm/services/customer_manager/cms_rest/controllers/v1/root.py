from cms_rest.controllers.v1.orm.root import OrmController
from pecan.rest import RestController


class V1Controller(RestController):
    orm = OrmController()
