class Error(Exception):
    pass


class ErrorStatus(Error):
    def __init__(self, status_code, message=None):
        self.status_code = status_code
        self.message = message


class NotFound(Error):
    def __init__(self, message=None, status_code=404):
        self.status_code = status_code
        self.message = message


class DuplicateEntryError(Error):
    def __init__(self, message=None, status_code=409):
        self.status_code = status_code
        self.message = message
