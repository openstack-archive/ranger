import uuidgen.controllers.v1.configuration as configuration
import uuidgen.controllers.v1.uuid_controller as v1
import uuidgen.controllers.v1.logs as logs


class RootController(object):
    # url/v1/
    uuids = v1.UUIDController()
    logs = logs.LogsController()
    configuration = configuration.ConfigurationController()
