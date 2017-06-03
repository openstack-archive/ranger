import wsme


class ClientSideError(wsme.exc.ClientSideError):
    def __init__(self, error, status_code=400):
        super(ClientSideError, self).__init__(error, status_code)


class JsonError(wsme.exc.ClientSideError):
    def __init__(self, status_code=400, message='incompatible JSON body'):
        super(JsonError, self).__init__(message, status_code)


class AuthenticationHeaderError(ClientSideError):
    def __init__(self, error, status_code=401,
                 message='Missing/expired/incorrect authentication header'):
        super(AuthenticationHeaderError, self).__init__(message, status_code)


class AuthenticationFailed(ClientSideError):
    def __init__(self, status_code=403,
                 message='The authenticated user is not allowed to create'
                         ' customers'):
        super(AuthenticationFailed, self).__init__(message, status_code)


class NotFound(ClientSideError):
    def __init__(self, status_code=404, message="Not Found"):
        super(NotFound, self).__init__(message, status_code)


class NoContent(ClientSideError):
    def __init__(self, status_code=204, message="Not Content"):
        super(NoContent, self).__init__(message, status_code)


class BusyError(ClientSideError):
    def __init__(self, status_code=409, message='Current resource is busy'):
        super(BusyError, self).__init__(message, status_code)


error_strategy = {
    '400': JsonError,
    '401': AuthenticationHeaderError,
    '403': AuthenticationFailed,
    '404': NotFound,
    '204': NoContent,
    '409': BusyError
}
