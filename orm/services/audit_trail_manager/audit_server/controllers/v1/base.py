"""base module for base wsme types and client side errors."""


import wsme
from wsme import types as wtypes


class ClientSideError(wsme.exc.ClientSideError):
    """base client side error."""

    def __init__(self, error, status_code=400):
        """init method..

        :param error: error message to show to the client.
        :param status_code: status code to show to the client.
        """
        super(ClientSideError, self).__init__(error, status_code)


class InputValueError(ClientSideError):
    """input value error."""

    def __init__(self, name, value, status_code=400):
        """init method..

        :param name: the input name for which an error was raised.
        :param value: the input value for which an error was raised.
        :param status_code: status code to show to the client.
        """
        super(InputValueError, self).__init__(
            "Invalid value for input {} : {}".format(name, value), status_code)


class EntityNotFoundError(ClientSideError):
    """entity not found error."""

    def __init__(self, entity_id):
        """init method..

        :param entity_id: the id for which an entity was not found.
        """
        super(EntityNotFoundError, self).__init__(
            "Entity not found for {}".format(entity_id), status_code=404)


class Base(wtypes.DynamicBase):
    """base class for wsme types."""

    pass
