"""transaction interface module."""


class Base(object):
    """transaction base class."""

    def __init__(self, url):
        """init method."""
        pass

    def add_record(self, transaction):
        """add new transaction record to the db."""
        raise NotImplementedError("Please Implement this method")

    def get_records(self, query):
        """get transactions that meet the given query from the db."""
        raise NotImplementedError("Please Implement this method")
