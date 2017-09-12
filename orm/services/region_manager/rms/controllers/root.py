from configuration import ConfigurationController
from lcp_controller import LcpController
from logs import LogsController
from orm.services.region_manager.rms.controllers.v2 import root

from pecan import expose


class RootController(object):
    lcp = LcpController()
    logs = LogsController()
    configuration = ConfigurationController()
    v2 = root.V2Controller()

    @expose(template='json')
    def _default(self):
        """Method to handle GET

            parameters: None
            return: dict describing lcp rest version information
        """
        return {
            "versions": {
                "values": [
                    {
                        "status": "stable",
                        "id": "v2",
                        "links": [
                            {
                                "href": "http://localhost:8080/"
                            }
                        ]
                    }
                ]
            }
        }
