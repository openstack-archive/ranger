import orm.services.id_generator.uuidgen.controllers.v1.configuration as configuration
import orm.services.id_generator.uuidgen.controllers.v1.logs as logs
import orm.services.id_generator.uuidgen.controllers.v1.uuid_controller as v1


class RootController(object):
    # url/v1/
    uuids = v1.UUIDController()
    logs = logs.LogsController()
    configuration = configuration.ConfigurationController()
