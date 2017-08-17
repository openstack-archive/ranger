from orm.services.customer_manager.cms_rest.controllers.v1 import root as v1
from pecan import expose


class RootController(object):
    # url/v1/
    v1 = v1.V1Controller()

    @expose(template='json')
    def _default(self):
        """Method to handle GET /
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
