from orm.root import OrmController
from pecan.rest import RestController


class V1Controller(RestController):
    orm = OrmController()
