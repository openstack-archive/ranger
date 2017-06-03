"""Exceptions module."""


class Error(Exception):
    pass


class ErrorStatus(Error):

    def __init__(self, status_code, message=""):
        self.status_code = status_code
        self.message = message


class NotFoundError(ErrorStatus):

    def __init__(self, status_code=404, message="Not found"):
        self.status_code = status_code
        self.message = message


class ConflictError(ErrorStatus):

    def __init__(self, status_code=409, message="Conflict error"):
        self.status_code = status_code
        self.message = message


class InputValueError(ErrorStatus):

    def __init__(self, status_code=400, message="value not allowed"):
        self.status_code = status_code
        self.message = message
