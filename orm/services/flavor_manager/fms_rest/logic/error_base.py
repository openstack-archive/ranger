
class Error(Exception):
    pass


class ErrorStatus(Error):

    def __init__(self, status_code, message=""):
        self.status_code = status_code
        self.message = message


class NotFoundError(ErrorStatus):

    def __init__(self, status_code=404, message="not found"):
        self.status_code = status_code
        self.message = message


class DuplicateEntityError(ErrorStatus):

    def __init__(self, status_code=409, message="item already exist"):
        self.status_code = status_code
        self.message = message


class ConflictError(ErrorStatus):

    def __init__(self, status_code=409, message="conflict error"):
        self.status_code = status_code
        self.message = message
