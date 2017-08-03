from OrdNotifier import root
from pecan import *
from pecan import expose
from webob.exc import status_map


class CatalogController(object):
    @expose()
    def index(self):
        return "Welcome to the catalog."


class ORD(object):
    @expose()
    def index(self):
        return dict()
    ord_notifier = root.OrdNotifier()


class RootOne(object):
    @expose()
    def index(self):
        return dict()
    ord = ORD()


class RootController(object):

    @expose(generic=True, template='index.html')
    def index(self):
        return dict()

    @index.when(method='GET')
    def index_get(self):
        return 'hi'

    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)

    cat = CatalogController()
    v1 = RootOne()
