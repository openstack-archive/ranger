from pecan import expose, redirect
from webob.exc import status_map
from lcp_controller import LcpController


class RootController(object):
    """
        in charge of RestAPI in the root directory
    """
    lcp = LcpController()

    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)
