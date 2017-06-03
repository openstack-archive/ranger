from ims.controllers.v1.orm.configuration import ConfigurationController
from ims.controllers.v1.orm.images.images import ImageController
from ims.controllers.v1.orm.logs import LogsController
from pecan.rest import RestController


class OrmController(RestController):

    configuration = ConfigurationController()
    images = ImageController()
    logs = LogsController()
