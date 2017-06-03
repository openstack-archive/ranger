import wsme
from pecan import response
from wsme import types as wtypes
import inspect


class ClientSideError(wsme.exc.ClientSideError):
    def __init__(self, error, status_code=400):
        response.translatable_error = error
        super(ClientSideError, self).__init__(error, status_code)


class InputValueError(ClientSideError):
    def __init__(self, name, value, status_code=400):
        super(InputValueError, self).__init__("Invalid value for input {} : {}".format(name, value), status_code)


class EntityNotFoundError(ClientSideError):
    def __init__(self, id):
        super(EntityNotFoundError, self).__init__("Entity not found for {}".format(id), status_code=404)


class Base(wtypes.DynamicBase):
    pass

    '''
    @classmethod
    def from_model(cls, m):
        return cls(**(m.as_dict()))

    def as_dict(self, model):
        valid_keys = inspect.getargspec(model.__init__)[0]
        if 'self' in valid_keys:
            valid_keys.remove('self')
        return self.as_dict_from_keys(valid_keys)


    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self, k))
                    for k in keys
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)

    @classmethod
    def from_db_and_links(cls, m, links):
        return cls(links=links, **(m.as_dict()))

    '''
