
class Error(Exception):
    pass


class InputError(Error):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class ErrorMesage(Error):
    def __init__(self, message=None):
        self.message = message


class ConflictValue(Error):
    """block values if operation still in progress"""
    pass
