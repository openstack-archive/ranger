from pecan import expose
from lcp_controller import LcpController
from logs import LogsController
from configuration import ConfigurationController
from rms.controllers.v2 import root


class RootController(object):
    lcp = LcpController()
    logs = LogsController()
    configuration = ConfigurationController()
    v2 = root.V2Controller()

    @expose(template='json')
    def _default(self):
        """
            Method to handle GET /
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
