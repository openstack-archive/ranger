"""Exceptions."""
import wsme
from wsme import types as wtypes


class ClientSideError(wsme.exc.ClientSideError):
    """return 400 with error message."""

    def __init__(self, error, status_code=400):
        """init function..

        :param error: error message
        :param status_code: returned code
        """
        super(ClientSideError, self).__init__(error, status_code)


class InputValueError(ClientSideError):
    """return 400 for invalid input."""

    def __init__(self, name, value, status_code=400):
        """init function.

        :param name: inavlid input field name
        :param value: invalid value
        :param status_code: returned code
        """
        super(InputValueError, self).__init__("Invalid "
                                              "value for input {} : "
                                              "{}".format(name, value),
                                              status_code)


class EntityNotFoundError(ClientSideError):
    """return 404 entity not found."""

    def __init__(self, id):
        """init func.

        :param id: Entity id
        """
        super(EntityNotFoundError, self).__init__("Entity not found "
                                                  "for {}".format(id),
                                                  status_code=404)


class LockedEntity(ClientSideError):
    """return 409 locked."""

    def __init__(self, name):
        """init func.

        :param name: locked message
        """
        super(LockedEntity, self).__init__("Entity {} is "
                                           "locked".format(name),
                                           status_code=409)


class NotAllowedError(ClientSideError):
    """return 405 not allowed operation."""

    def __init__(self, name):
        """init func.

        :param name: name of method
        """
        super(NotAllowedError, self).__init__("not allowed : "
                                              "{}".format(name),
                                              status_code=405)


class Base(wtypes.DynamicBase):
    """not implemented."""

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
