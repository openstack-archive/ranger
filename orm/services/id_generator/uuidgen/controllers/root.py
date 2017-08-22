import logging

import orm.services.id_generator.uuidgen.controllers.v1.root as root
from pecan import expose
from pecan.rest import RestController

LOG = logging.getLogger(__name__)


class RootController(RestController):
    # url/v1/
    v1 = root.RootController()

    @expose(template='json')
    def get(self):
        """Method to handle GET /
            parameters: None
            return: dict describing uuid command version information
        """
        LOG.info("root -get versions")
        return {
            "versions": {
                "values": [
                    {
                        "status": "stable",
                        "id": "v1",
                        "links": [
                            {
                                "href": "http://localhost:8090/"
                            }
                        ]
                    }
                ]
            }
        }
