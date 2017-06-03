from pecan import expose, request, response
from webob.exc import status_map
from pecan.secure import SecureController
from cms_rest.controllers.v1 import root as v1
from cms_rest.utils import authentication
from pecan import conf


class RootController(object):
    # url/v1/
    v1 = v1.V1Controller()

    @expose(template='json')
    def _default(self):
        """
            Method to handle GET /
            parameters: None
            return: dict describing cms rest version information
        """
        return {
            "versions": {
                "values": [
                    {
                        "status": "stable",
                        "id": "v1",
                        "links": [
                            {
                                "href": "http://localhost:7080/"
                            }
                        ]
                    }
                ]
            }
        }
