import wsme


class ClientSideError(wsme.exc.ClientSideError):
    def __init__(self, error, status_code=400):
        super(ClientSideError, self).__init__(error, status_code)


class NoContent(ClientSideError):
    def __init__(self, status_code=204, message="No Content"):
        super(NoContent, self).__init__(message, status_code)


class JsonError(wsme.exc.ClientSideError):
    def __init__(self, status_code=400, message="incompatible JSON body"):
        super(JsonError, self).__init__(message, status_code)


class AuthenticationHeaderError(ClientSideError):
    def __init__(self, error, status_code=401, message="Missing/expired/incorrect authentication header"):
        super(AuthenticationHeaderError, self).__init__(message, status_code)


class AuthenticationFailed(ClientSideError):
    def __init__(self, status_code=403, message="The authenticated user is not allowed to create customers"):
        super(AuthenticationFailed, self).__init__(message, status_code)


class NotFound(ClientSideError):
    def __init__(self, status_code=404, message="The specific transaction was not found", **kw):
        super(NotFound, self).__init__(message, status_code)


class MethodNotAllowed(ClientSideError):
    def __init__(self, status_code=405, message="This method is not allowed. Please use update flavor instead", **kw):
        super(MethodNotAllowed, self).__init__(message, status_code)


class BusyError(ClientSideError):
    def __init__(self, status_code=409, message="Current resource is busy"):
        super(BusyError, self).__init__(message, status_code)


class ConflictValueError(ClientSideError):
    def __init__(self, message="conflict value error", status_code=409):
        super(ConflictValueError, self).__init__(message, status_code)


class DuplicateFlavorError(ClientSideError):
    def __init__(self, status_code=409):
        super(DuplicateFlavorError, self).__init__("Flavor already exists",
                                                   status_code)


error_strategy = {
    '204': NoContent,
    '400': JsonError,
    '401': AuthenticationHeaderError,
    '403': AuthenticationFailed,
    '404': NotFound,
    '405': MethodNotAllowed,
    '409': BusyError,
    '409.1': DuplicateFlavorError
}
