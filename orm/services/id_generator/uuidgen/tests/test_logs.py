"""Set log level module unittests."""

# import mock
# from mock import patch
from uuidgen.controllers.v1 import logs
# import logging
from uuidgen.tests import FunctionalTest


class TestLogs(FunctionalTest):
    """Main test case."""

    def test_change_log_level_sanity(self):
        logs.__name__ = 'test.test'
        response = self.app.put('/v1/logs', 'level=DEBUG')

    def test_change_log_level_bad_log_level(self):
        logs.__name__ = 'test'
        response = self.app.put('/v1/logs', 'level')
