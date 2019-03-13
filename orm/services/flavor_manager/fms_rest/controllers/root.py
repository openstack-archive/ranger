import orm.base_config as config

from orm.services.flavor_manager.fms_rest.controllers.v1.v1 import V1Controller
from pecan import expose
from webob.exc import status_map


class RootController(object):
    v1 = V1Controller()

    @expose(template='json')
    def get(self):
        """Method to handle GET /
            prameters: None
            return: dict describing flavor command version information
        """

        return {
            "versions": {
                "values": [
                    {
                        "orm": "stable",
                        "id": "v1",
                        "links": [
                            {
                                "href": config.fms['base_url']
                            }
                        ]
                    }
                ]
            }
        }

    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)
