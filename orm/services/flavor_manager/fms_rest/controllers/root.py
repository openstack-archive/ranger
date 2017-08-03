from fms_rest.controllers.v1.v1 import V1Controller
from pecan import conf, expose
from webob.exc import status_map


class RootController(object):
    v1 = V1Controller()

    '''
    @classmethod
    def check_permissions(cls):
        # Extract the required values from the request header
        headers = request.headers
        token_to_validate = headers.get('X-Auth-Token')
        lcp_id = headers.get('X-Auth-Region')
        return authentication.check_permissions(conf, token_to_validate, lcp_id)
    '''
    @expose(template='json')
    def get(self):
        """
            Method to handle GET /
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
                                "href": conf.application_root
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
