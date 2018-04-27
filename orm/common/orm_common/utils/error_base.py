
class Error(Exception):
    pass


class ErrorStatus(Error):

    def __init__(self, status_code, message=""):
        self.message = message
