"""Set log level module unittests."""

# import mock
# from mock import patch
from orm.services.id_generator.uuidgen.controllers.v1 import logs
from orm.tests.unit.uuidgen import FunctionalTest


class TestLogs(FunctionalTest):
    """Main test case."""

    def test_change_log_level_sanity(self):
        logs.__name__ = 'test.test'
        response = self.app.put('/v1/logs', 'level=DEBUG')

    def test_change_log_level_bad_log_level(self):
        logs.__name__ = 'test'
        response = self.app.put('/v1/logs', 'level')
